@Library('shared-pipelines') _


def assumeRole() {
    sh "aws sts assume-role \
        --role-arn arn:aws:iam::003966386768:role/JenkinsSlave \
        --region ap-southeast-2 \
        --role-session-name JenkinsPython > /dev/null "
}



pipeline {
    agent {
      kubernetes {
        label 'invoke-databricks-wheel-tasks-lib'
        defaultContainer 'python-deployment'
        yaml """
            metadata:
              namespace: jenkins
              labels:
                app-label: invoke-databricks-wheel-tasks-lib
            spec:
              serviceAccountName: jenkins-sa
              securityContext:
                runAsUser: 0
              tolerations:
              - key: "sparklecore.net/grouping"
                operator: "Equal"
                value: "jenkins"
                effect: "NoExecute"
              nodeSelector:
                sparklecore.net/grouping: jenkins
              containers:
              - name: python-deployment
                image: ${AWS_SHRD_REGISTRY_URL}/${PYTHON_DEPLOYMENT}:${PYTHON_DEPLOYMENT_VERSION}
                resources:
                  limits:
                    memory: 1Gi
                  requests:
                    memory: 0.5Gi
                    cpu: 0.2
                tty: true
        """
    }
  }

  environment {
    PATH = "$HOME/.poetry/bin:${env.PATH}"
  }

  stages {
      stage('Configure Credentials') {
          steps {
              script {
                  awsHelperEKS.initProfile()
                  assumeRole()

              }
          }
      }

      stage('Setup tooling') {
          steps {
              script {
                sh "python -m pip install --upgrade pip"
                sh "python -m pip install --upgrade poetry"
                sh "poetry config virtualenvs.in-project true"
                sh "poetry install"
                sh "poetry run invoke --list"

              }
          }
      }

      stage('Quality Assurance') {
          steps {
              script {
                sh "poetry run invoke lint"
                sh "poetry run invoke typecheck"
                sh "poetry run invoke test"
                sh "poetry build --format wheel"
              }
          }
      }

      stage('Publishing') {

          when {
            buildingTag()
          }

          steps {
              script {
                // https://python-poetry.org/docs/repositories/#using-a-private-repository
                def NEXUS_USERNAME = "jenkins"
                def NEXUS_PASSWORD_CMD = """
                      aws secretsmanager get-secret-value \
                      --profile svc \
                      --region ap-southeast-2 \
                      --secret-id infra/jenkins/nexus-secret | jq -r .SecretString"""
                def NEXUS_PASSWORD = sh(script: NEXUS_PASSWORD_CMD, returnStdout: true)
                withSecretEnv([
                    [var: "NEXUS_PASSWORD", password: NEXUS_PASSWORD],
                    [var: "NEXUS_USERNAME", password: NEXUS_USERNAME]
                  ]) {
                  sh(script: '''
                    poetry config --local http-basic.nexus ${NEXUS_USERNAME} ${NEXUS_PASSWORD}
                  ''', returnStdout: false)
                }
                sh "poetry publish --dry-run --repository nexus"
              }
          }
      }
  }
}
