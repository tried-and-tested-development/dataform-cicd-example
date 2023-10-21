import requests

import click
import google.auth
from google.cloud import dataform_v1beta1


def create_compilation_result(project_id, region, repo, branch, schema_suffix=None):

    parent = f'projects/{project_id}/locations/{region}/repositories/{repo}'

    # Create a client
    client = dataform_v1beta1.DataformClient()

    # Initialize request argument(s)
    compilation_result = dataform_v1beta1.CompilationResult()
    compilation_result.git_commitish = branch
    compilation_result.code_compilation_config.default_database = project_id

    if schema_suffix is not None:
        compilation_result.code_compilation_config.schema_suffix = schema_suffix

    request = dataform_v1beta1.CreateCompilationResultRequest(
        parent=parent,
        compilation_result=compilation_result,
    )

    # Make the request
    response = client.create_compilation_result(request=request)

    print(response)

    # Handle the response
    return response


def refresh_release_configuration(
        project_id,
        region,
        repo,
        release_config_name,
        branch):

    credentials, _ = google.auth.default()

    auth_req = google.auth.transport.requests.Request()

    credentials.refresh(auth_req)  # refresh token
    token_str = credentials.token  # prints token

    # Get latest config
    headers_req = {'Authorization': 'Bearer ' + token_str}
    url = f"https://dataform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/repositories/{repo}/releaseConfigs/{release_config_name}"
    resp = requests.get(url=url, headers=headers_req)

    if resp.status_code != 200:
        raise RuntimeError(resp.content)

    url = f"https://dataform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/repositories/{repo}/releaseConfigs/{release_config_name}"
    resp = requests.patch(url=url, json=resp.json(), headers=headers_req)

    if resp.status_code != 200:
        raise RuntimeError(resp.content)


def create_workflow_invocation(project_id, region, repo, compile_result):

    parent = f'projects/{project_id}/locations/{region}/repositories/{repo}'

    # Create a client
    client = dataform_v1beta1.DataformClient()

    # Initialize request argument(s)
    request = dataform_v1beta1.CreateWorkflowInvocationRequest(
        parent=parent,
        workflow_invocation={'compilation_result': compile_result}
    )

    # Make the request
    resp = client.create_workflow_invocation(request=request)


@click.command()
@click.option('--project_id', prompt='Project ID', help='The Google Cloud project id.')
@click.option('--region', prompt='Region', default='us-east1', help='Region the Dataform environment is in.')
@click.option('--repo', prompt='Repo', help='Dataform repo name.')
@click.option('--branch', default='prod', help='Repo branch to compile against.')
@click.option('--schema_suffix', default=None, help='Schema suffix used.')
@click.option('--release_config', prompt='Release config name', help='Dataform release config to refresh.')
@click.option('--run_compiled_workflow', default=False, help='Run workflow invocation.', type=bool)
def cli(project_id, region, repo, branch, schema_suffix, release_config, run_compiled_workflow):
    """Deployment CLI for dataform."""

    response = create_compilation_result(
        project_id=project_id,
        region=region,
        repo=repo,
        branch=branch,
        schema_suffix=schema_suffix
    )

    refresh_release_configuration(
        project_id=project_id,
        region=region,
        repo=repo,
        release_config_name=release_config,
        branch=branch)

    if run_compiled_workflow:
        create_workflow_invocation(
            project_id=project_id,
            region=region,
            repo=repo,
            compile_result=response.name)


if __name__ == '__main__':
    cli()
