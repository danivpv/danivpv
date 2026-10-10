# Deployment Troubleshooting & Senior Log Triaging Methodology

This document is a pedagogic reference capturing the real-world deployment challenges encountered while building the production ML Platform on AWS ECS Fargate, along with the methodologies used by Senior Forward Deployed Engineers (FDEs) and Platform Engineers to diagnose and resolve them without getting lost in thousands of lines of logs.

---

## 1. Catalog of Real-World Deployment Errors & Root Causes

### A. The Virtualenv Shebang Relocation Bug (`exec: mlflow: not found`)
* **Symptom**: ECS container crashes immediately on startup with `exited with code 127` and the CloudWatch log: `sh: 1: exec: mlflow: not found`.
* **The Root Cause**: When installing Python tools via `pip` or `uv` into a virtual environment (`.venv`), console scripts (like `mlflow`, `pytest`, `ruff`, or `uvicorn`) are generated with a hardcoded **shebang (`#!`)** on line 1 pointing to the exact builder path where they were compiled:
  ```text
  #!/build/.venv/bin/python
  ```
  When Stage 2 of a multi-stage Docker build copied `/build/.venv` to `/app/.venv`, the file `/app/.venv/bin/mlflow` still contained `#!/build/.venv/bin/python`. When POSIX `sh` tried to execute `mlflow`, the Linux kernel failed to find `/build/.venv/bin/python`, returning `ENOENT` (No such file or directory) which `sh` reports as `not found` (exit code 127).
* **Why `oversight/src/rag/rag/runtime/Dockerfile` Was Immune**:
  If you examine the RAG service Dockerfile, notice how Stage 2 is structured:
  ```dockerfile
  # Lambda demands a flat layout: copy everything straight into the task root
  COPY --from=builder /build/.venv/lib/python3.12/site-packages ${LAMBDA_TASK_ROOT}/
  CMD ["rag.rag.runtime.main.handler"]
  ```
  1. **Site-Packages Flattening**: RAG builds for AWS Lambda. Instead of copying the `/bin` directory containing console scripts with shebangs, it only copies the raw Python library files (`site-packages`) directly into the root.
  2. **Native RIC Import**: Lambda does not execute shell commands via `sh -c`. The AWS Lambda Runtime Interface Client (C/C++ runtime) directly loads `rag.rag.runtime.main.handler` as a Python module in memory.
  *Note: Had you migrated RAG to ECS using `WORKDIR /build` to `WORKDIR /app` as described in the blueprint comments, running `uvicorn` as a shell script would have triggered the exact same shebang crash!*
* **The Universal Solution**:
  Always align the `WORKDIR` between build and runtime stages (`WORKDIR /app` in Stage 1 and Stage 2). Furthermore, prefer executing `python -m <module>` (e.g., `exec python -m mlflow server`) which invokes the binary directly and bypasses script shebangs entirely.

---

### B. CDK Docker Build Context Scoping (`/uv.lock: not found`)
* **Symptom**: Running `cdk deploy` or `cdk synth` fails during the asset bundling phase with: `ERROR: failed to calculate checksum of ref ...: "/uv.lock": not found`.
* **The Root Cause**: In AWS CDK, when configuring a `DockerImageAsset`, setting `directory="src/ml_platform/experiment_tracking/runtime"` scopes the Docker daemon's build context strictly to that folder. When the Dockerfile attempted `COPY --mount=type=bind,source=uv.lock,target=uv.lock`, Docker could not see `uv.lock` or `pyproject.toml` located at the repository root.
* **The Solution**: Always set the CDK build context to the project root (`directory=_ROOT_DIR`) and point to the Dockerfile using the `file=` parameter:
  ```python
  mlflow_image = DockerImageAsset(
      self, "MlflowImage",
      directory=_ROOT_DIR,
      file="src/ml_platform/experiment_tracking/runtime/Dockerfile",
  )
  ```

---

### C. Missing Transitive Dependencies (`ModuleNotFoundError: 'pkg_resources'`)
* **Symptom**: ECS container starts, Python executes, but crashes with a traceback ending in `ModuleNotFoundError: No module named 'pkg_resources'`.
* **The Root Cause**: Modern slim Python container images (`python:3.12-slim`) do not pre-install legacy packaging utilities like `setuptools`. Many older ML and telemetry libraries (or their transitive dependencies) still import `pkg_resources` at runtime. Using ad-hoc `pip install` without comprehensive lockfiles often misses these implicit dependencies.
* **The Solution**: Use multi-stage `uv sync --frozen --group <domain>` from a centralized lockfile (`uv.lock`), ensuring all required transitive dependencies (including `setuptools` when required by MLflow or AzureML core) are deterministically compiled and baked into `/app/.venv`.

---

### D. ECS Deployment Circuit Breaker (`GeneralServiceException`)
* **Symptom**: CloudFormation stack hangs in `UPDATE_IN_PROGRESS` or `CREATE_IN_PROGRESS` for 10+ minutes, then fails with: `Resource handler returned message: "Error occurred during operation 'ECS Deployment Circuit Breaker was triggered'."` followed by `ROLLBACK_COMPLETE`.
* **The Root Cause**: AWS Fargate monitors new task deployments. If tasks repeatedly crash on startup (e.g., due to exit code 127 from shebang errors or exit code 1 from `ModuleNotFoundError`), the ECS circuit breaker halts deployment to prevent cascading outages and rolls back the CloudFormation stack.

---

### E. AWS EC2 Security Group Non-ASCII Description Rejection (`400 InvalidRequest`)
* **Symptom**: CloudFormation stack fails immediately during resource creation with: `CREATE_FAILED | AWS::EC2::SecurityGroup ... Resource handler returned message: "Value (...) for parameter GroupDescription is invalid. Character sets beyond ASCII are not supported. (Service: Ec2, Status Code: 400..."` followed by stack rollback.
* **The Root Cause**: The AWS EC2 `CreateSecurityGroup` API enforces strict 7-bit ASCII (characters 0–127) validation on the `GroupDescription` parameter. In Python IDEs or markdown-formatted comments, developers often accidentally use typographic characters like the **em-dash (`—`, Unicode U+2014)** or en-dash (`–`, Unicode U+2013) instead of a standard ASCII hyphen (`-`). When CDK synthesizes and submits this template, EC2 rejects the payload with HTTP 400 `InvalidRequest`.
* **The Solution**: Keep all AWS infrastructure metadata, security group descriptions, and IAM resource descriptions strictly within standard ASCII. When debugging CDK syntheses, run a quick grep across your infrastructure definitions for non-ASCII typography:
  ```bash
  grep -P "[^\x00-\x7F]" src/ml_platform/**/infrastructure.py
  ```

---

### F. Feast YAML Comment Apostrophe Bug (`os.path.expandvars` Quote Trapping)
* **Symptom**: Running `feast apply` against AWS S3 fails with `botocore.exceptions.ParamValidationError: Invalid bucket name "${feature_bucket}"`, even though `export FEATURE_BUCKET=...` is correctly set in your shell.
* **The Root Cause**: When Feast initializes a feature repository, it executes Python's `os.path.expandvars()` on the entire string contents of `feature_store.yaml` to substitute environment variables. When a YAML comment contains an unmatched single quote or apostrophe (for example: `# offline_store.type = "file": Feast's file provider reads Parquet`), Python's variable expander treats every character following that apostrophe as being inside an open single-quoted string literal! In Bash and Python syntax, variables inside single quotes (`'...'`) are ignored and never expanded. Consequently, `s3://${FEATURE_BUCKET}/...` is left as literal text, which boto3 converts to lowercase `"${feature_bucket}"` and rejects.
* **The Solution**: Never use contractions, unmatched single quotes/apostrophes, or special typographic characters (like em-dashes) in YAML configuration files or their comments. Keep configs strictly ASCII and quote-balanced.

---

### G. Feast DynamoDB Online Store Schema Validation (`table_name` vs `table_name_template`)
* **Symptom**: Running `feast apply` crashes immediately with `pydantic.ValidationError: 1 validation error for DynamoDBOnlineStoreConfig ... Extra inputs are not permitted [type=extra_forbidden]`.
* **The Root Cause**: Feast defines strict Pydantic v2 models for its infrastructure providers. For the DynamoDB online store (`DynamoDBOnlineStoreConfig`), the configuration field `table_name` does not support dynamic environment variable templating. When deploying dynamic cloud environments where DynamoDB tables are generated by CDK, Feast requires the specific schema attribute `table_name_template`.
* **The Solution**: In `feature_store.yaml`, use `table_name_template: ${ONLINE_TABLE}` when referencing dynamic table names.

---

### H. Feast SQLite Compatibility Validation Bug (`project` name with hyphens)
* **Symptom**: In an AWS S3 + DynamoDB feature repository, running `feast apply` throws `pydantic.ValidationError: Project names for SQLite cannot contain hyphens`.
* **The Root Cause**: In Feast >= 0.64 with Pydantic v2, field validators are evaluated before union type resolution completes. When `project: ml-platform` contains a hyphen (`-`), Feast's legacy SQLite schema validator is erroneously triggered during model parsing, even when configured for AWS S3 and DynamoDB.
* **The Solution**: Always use underscores instead of hyphens for Feast project names (e.g., `project: ml_platform`).

---

### I. Shell Quoting Nightmares with Inline Scripts (`python -c "..."`)
* **Symptom**: When running multi-line inline Python scripts in Git Bash or Windows PowerShell, the command crashes with syntax errors, unexpected string truncation, or `ModuleNotFoundError`, or hangs waiting for unmatched quotes.
* **The Root Cause**: Multi-line strings passed to `-c "..."` cause severe shell escaping conflicts across different operating systems. In Git Bash (MINGW64) and PowerShell, double quotes (`"`) and single quotes (`'`) interact unpredictably with shell environment variable expansion (`$VAR`), newlines, and Python f-strings.
* **The Solution**: Never use inline multi-line Python scripts in documentation or deployment workflows. Always create standalone, version-controlled scripts inside the `scripts/` directory (e.g., `scripts/test_historical_features.py`) and invoke them cleanly via `uv run ... python scripts/<script_name>.py`.

---

### J. ECS Task ARN Collisions in Shell Variables (`TASK_ARN` vs `MLFLOW_TASK_ARN` vs `TRAIN_TASK_ARN`)
* **Symptom**: Running `aws ecs wait tasks-stopped --cluster "$CLUSTER" --tasks "$TASK_ARN"` hangs for 10+ minutes and then fails with `Waiter TasksStopped failed: Max attempts exceeded`, while `exitCode` returns `None`.
* **The Root Cause**: In interactive shell sessions, reusing a generic environment variable like `TASK_ARN` across different deployment steps causes silent target collisions. When checking the MLflow server IP in Step 4, `TASK_ARN` is assigned to the MLflow Fargate web server task. If `TASK_ARN` is subsequently referenced during Step 8 training verification without being explicitly reassigned to the new training task, the AWS waiter attempts to wait for the long-running MLflow web server to terminate. Because the MLflow web server runs continuously (`RUNNING` state), the waiter eventually times out, and querying for an exit code returns `None`.
---

### K. Security Group Packet Drops & IGW Hairpinning (`ConnectTimeoutError` on MLflow Port 5000)
* **Symptom**: In an ECS Fargate training or inference task, logs show repeated retries and connection timeouts: `Retrying (...) after connection broken by 'ConnectTimeoutError(<HTTPConnection(host='44.223.15.226', port=5000) at ...>, 'Connection to 44.223.15.226 timed out. (connect timeout=120)')'`.
* **The Root Cause**: This occurs due to a two-fold networking mismatch:
  1. **Missing Security Group Ingress Rules**: The MLflow security group (`mlflow_sg`) was configured to allow inbound traffic only from the developer's external IP address (`developer_cidr`), omitting rules to allow port 5000 from the Training Task SG (`training.task_sg`) and Inference Task SG (`inference.task_sg`).
  2. **IGW Hairpinning & Security Group Striping**: When containers inside an AWS VPC connect to a service using its **Public IP address** (`http://44.xxx:5000`), the traffic routes out through the AWS Internet Gateway (IGW) and hairpins back into the VPC. When returning from the IGW, AWS strips internal security group metadata (`source_security_group_id`), making the traffic appear as originating from an external public IP address rather than an internal VPC security group.
* **The Solution**:
  1. Add explicit `CfnSecurityGroupIngress` rules in CDK allowing port 5000 on `mlflow_sg` from `training.task_sg` and `inference.task_sg`.
  2. In deployment runbooks, store the MLflow server's **Private IP address** (`http://${PRIVATE_IP}:5000`) in SSM Parameter Store (`/ml-platform/sandbox/mlflow-tracking-uri`) so that Fargate containers communicate strictly over the internal VPC network fabric.

---

### L. DynamoDB Asynchronous Tag Propagation Locking (`LimitExceededException`)
* **Symptom**: Running `feast apply` immediately after deploying infrastructure via `make deploy` fails with: `botocore.errorfactory.LimitExceededException: An error occurred (LimitExceededException) when calling the TagResource operation: Subscriber limit exceeded: Table tags are being updated: MLPlatformStateful-FeatureStoreOnlineStore...`.
* **The Root Cause**: When AWS CloudFormation creates or updates a DynamoDB table with tags, AWS initiates an asynchronous background process to apply those tags across all storage partitions of the table. While AWS is actively processing a tag update on a DynamoDB table, any API call to `TagResource` or `UntagResource` on that table is rejected with `LimitExceededException: Table tags are being updated`. When Feast's online store provider connects to DynamoDB during `feast apply`, it automatically attempts to call `tag_resource(...)` to attach metadata tags (`feast-project: ml_platform`). Because CloudFormation's background tag propagation had not fully settled yet, AWS rejected the request.
* **The Solution**: This is a transient eventual consistency lock in real-world infrastructure pipelines. Simply wait 30 to 60 seconds after CloudFormation stack creation/update finishes before running `feast apply`, allowing DynamoDB's background tag propagation to settle.

---

## 2. Senior Log Triaging Methodology: How to Read Thousands of Lines of Logs

When facing a failed CI/CD pipeline, a rolled-back CloudFormation stack, or a crashing Kubernetes/ECS cluster, human engineers cannot read 10,000 lines of logs chronologically. Senior engineers use structured **filtering, categorization, and pattern recognition** to pinpoint root causes in seconds.

### Step 1: Work Backward from Terminal State Transitions
Never start reading from line 1. Scroll directly to the bottom of the log output or query the end of the stream. Look for the **terminal failure event** that triggered the abort:
* In CDK / CloudFormation: Search for `CREATE_FAILED`, `UPDATE_FAILED`, or `ROLLBACK_IN_PROGRESS`.
* In Docker builds: Search for `ERROR:` or `failed to solve:`.

### Step 2: Decode the Exit Code Language
When a container terminates, the kernel assigns a numeric exit status. Memorizing these numbers instantly narrows your debugging scope before you even open a log file:
* **Exit Code `0`**: Clean, intended shutdown.
* **Exit Code `1`**: Application runtime exception (e.g., unhandled Python `Traceback`, missing environment variable, database connection refusal). *Action: Search CloudWatch logs for `Traceback (most recent call last)` or `Exception:`.*
* **Exit Code `127`**: Command not found (`ENOENT`). The kernel could not locate the binary or executable script specified in `CMD` or `ENTRYPOINT`, OR the script's shebang (`#!/path/to/python`) points to a non-existent directory. *Action: Inspect Dockerfile `PATH`, shebang paths, and `WORKDIR` alignment.*
* **Exit Code `137`**: `SIGKILL` (Immediate forced termination). Almost always caused by the **Linux OOM (Out of Memory) Killer**. Your container exceeded its allocated ECS Memory limit (e.g., loading a 4GB model into a 2GB Fargate task). *Action: Double memory allocation in CDK (`memory_limit_mib`).*
* **Exit Code `143`**: `SIGTERM` (Graceful termination requested). ECS is shutting down the task because CloudFormation initiated a rollback, auto-scaling scaled in, or a new deployment replaced the task. *This is usually a symptom of a rollback, not the root cause itself.*

### Step 3: The "Three-Query" CloudWatch Search Protocol
When checking Fargate container logs in AWS CloudWatch Logs Insights or the AWS Console, execute these three filtering steps:
1. **Filter by Error Keywords**: Search the log group using terms:
   `"Traceback" | "Error" | "Exception" | "not found" | "fatal"`
2. **Isolate by Task ID**: If multiple tasks are spinning up and dying during a deployment loop, grab the Task ID of the single stopped container from ECS and filter logs exclusively by that log stream.
3. **Inspect the Seconds Before Exit**: Look at the timestamps. If the task died at `20:14:15`, read the 5 log lines generated between `20:14:13` and `20:14:15`. That is where the stack trace lives.

### Step 4: Shift-Left Verification (Fail Early, Fail Fast)
Why wait 15 minutes for CloudFormation to push images to ECR, provision Fargate tasks, trigger a circuit breaker, and rollback when you can verify in 5 seconds?
* **Local Image Compilation (`make docker-build`)**: Compiling images locally immediately catches build syntax errors, lockfile desynchronization, missing build contexts, and shebang path misalignments before AWS is ever contacted.
* **Local Container Smoke Testing**: When debugging complex startup crashes, run the built container locally with mock environment variables to verify binary execution:
  ```bash
  docker run --rm ml-platform/mlflow:latest sh -c "which mlflow && python -m mlflow --version"
  ```

---

## 3. The Platform Engineer's & ML Engineer's Mental Model: From Script to Production System

When transitioning from building local Jupyter notebooks or single-script ML models to designing cloud-native production ML platforms, your engineering mental model must evolve around three foundational pillars: **Data Contract Separation**, **Infrastructure as Code (IaC) Decoupling**, and **The Cloud Debugging Feedback Loop**.

### A. Why a Feature Store? Understanding the Dual-Store Architecture (Offline vs. Online)
In traditional data science, feature engineering is often embedded inside training scripts (`df["feature"] = ...`). When moving to production inference, engineering teams often re-implement those same transformations in Java, C++, or Go for a real-time backend. This duplication introduces **train-serve skew**: subtle discrepancies between how features were calculated during training vs. how they are computed at scoring time, leading to silent model degradation.

A production Feature Store like **Feast** solves this by enforcing a **Dual-Store Architecture**:
1. **The Offline Store (S3 Parquet Data Lake)**: Designed for high-throughput batch reads over historical time series. When training models, Scikit-Learn or XGBoost needs millions of records across months of history. S3 FileProvider reads columnar Parquet files directly into memory.
2. **The Online Store (AWS DynamoDB)**: Designed for single-digit millisecond key-value lookups (`PAY_PER_REQUEST` on-demand billing). When a batch inference scheduler or real-time application needs to score a specific customer, it cannot scan months of S3 files. It looks up the entity key (`entity_id`) in DynamoDB to get the current feature state instantly.
3. **Point-in-Time Correct Joins (Data Leakage Prevention)**: Why is Step 6 in our deployment guide so important? In ML engineering, **data leakage** occurs when future information accidentally contaminates historical training data (for example, using a customer's account balance from Friday to predict whether they churned on Wednesday). Feast's point-in-time join engine strictly aligns entity timestamps against feature observation timestamps, ensuring your training dataframe only sees features that existed *at or before* the exact second the event occurred.

### B. Decoupling Infrastructure from Runtime Logic
In a professional cloud engineering team, platform infrastructure and machine learning business logic evolve at different speeds:
* **Infrastructure (CDK in `src/ml_platform/*/infrastructure.py`)**: Defines the immutable cloud hardware, networking, security groups, IAM least-privilege roles, S3 buckets, and DynamoDB tables. This layer moves slowly and requires high rigor. Notice that we **never hardcode AWS names**. CDK generates unique physical names (e.g., `MLPlatformStateful-FeatureStoreOnlineStore...`) and injects them dynamically into runtime containers as environment variables.
* **Runtime Logic (`train.py`, `predict.py`, Feast definitions)**: Consumes those environment variables via fail-fast Pydantic contracts (`TrainingConfig`, `InferenceConfig`). If an environment variable is missing, the container fails immediately at startup (fail-fast) rather than running for 30 minutes before crashing when trying to connect to AWS.
* **Why this separation matters**: Because our infrastructure simply provides container execution environments with standardized IAM permissions and environment variables, you can update your machine learning models, tweak feature engineering formulas, or upgrade Scikit-Learn versions without ever modifying or redeploying the AWS cloud infrastructure stack!

### C. Embracing the Cloud Debugging Feedback Loop
In cloud engineering, encountering bugs like the virtualenv shebang crash, Pydantic schema mismatches, or YAML comment apostrophe trapping is not a sign of failure—it is the normal engineering cycle of working with complex distributed systems. Senior Forward Deployed Engineers (FDEs) excel not by avoiding errors, but by systematically reducing the **Mean Time to Diagnosis (MTTD)**:
1. **Never guess; read the ground truth**: Whether it is an AWS SDK validation error, an ECS circuit breaker rollback, or a local container traceback, the log output always contains the exact mechanical reason for failure. Use the filtering methodologies in Section 2 to strip away the noise.
2. **Isolate the boundary**: When a command fails, determine whether the failure is in the **local shell environment** (e.g., unexpanded bash variables, Windows line endings, relative imports), the **container build layer** (lockfiles, shebang paths), or the **cloud infrastructure layer** (IAM permissions, DynamoDB limits, EC2 ASCII restrictions).
3. **Document and codify lessons**: Every time you spend an hour debugging a subtle issue (like an em-dash in a security group description or an apostrophe in a YAML comment), document it immediately in team runbooks and system prompts so that automated CI/CD pipelines, fellow engineers, and AI coding assistants never repeat the same mistake twice.
