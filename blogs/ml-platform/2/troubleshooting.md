# Part 2 — Deployment Troubleshooting and Production Bugs

This document logs the production bugs encountered during the deployment of the API and Catalog database, serving as source material for "The Ugly Part" of the blog post.

## 1. The Alembic Collision (RDS Race Condition)

**The Bug:**
To save on AWS costs, we deployed a single `db.t4g.micro` RDS instance to serve as the backend for *both* the MLflow Tracking Server and the new FastAPI Model Catalog. Both MLflow and our custom FastAPI app use SQLAlchemy and Alembic for database migrations.

When the API container booted, our `alembic upgrade head` command failed. It collided with the `alembic_version` table that MLflow automatically creates when it initializes its own backend store. Because both tools were trying to manage schema versions using the default `alembic_version` table name, the migrations deadlocked and corrupted the state.

**The Fix:**
1. **Isolated Version Tables:** We customized the `src/ml_platform/api/runtime/alembic/env.py` script. By injecting `version_table="api_alembic_version"` into the `context.configure()` block, we isolated the API's migration history from MLflow's history.
   
2. **Deterministic Boot Sequence:** We created `src/ml_platform/api/runtime/entrypoint.sh` and modified the FastAPI `Dockerfile` to execute it. This script forces the container to run `alembic upgrade head` synchronously *before* executing `uvicorn`, ensuring the API schema exists before any traffic is served.

3. **The Nuke Option:** Because the initial race condition corrupted the RDS schema state (MLflow created tables while the API was crashing), we had to run `cdk destroy` and completely redeploy the infrastructure to untangle the database state and validate the fix.
