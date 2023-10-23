# dataform-cicd-example

## Python
- [deploy.py](./python/deploy.py) A command line utility used to trigger dataform commands in a CICD process.

## Cloudbuild
```yaml
# Run Dataform Invocation
steps:
 - name: python
   entrypoint: python
   args: ['-m', 'pip', 'install', 'google-cloud-dataform', 'click', '--user']
 - name: 'python'
   entrypoint: 'bash'
   args:
     - '-c'
     - |
       python deploy.py \
       --project_id "${_PROJECT_ID}" \
       --region "${_REGION}" \
       --repo "${_REPO}" \
       --branch "${_BRANCH}" \
       --schema_suffix "${_SCHEMA_SUFFIX}" \
       --release_config "${_RELEASE_CONFIG}" \
       --run_compiled_workflow ${_RUN_COMPILED_WORKFLOW}
```
