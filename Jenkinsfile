String DOCKER_REGISTRY = "wh-imaging-dev-docker-local.artifactory.swg-devops.com"
String BUILD_UTIL_IMAGE = "whi-image-python37-build-util:latest"
String VERSION = "3.0.0"
String SLACK_CHANNEL = "#whi-caf-builds"
boolean NOTIFY_PR_IN_SLACK = true
String MAINLINE_BRANCH = "master"
String GIT_REPO = 'WH-Imaging/whi-caf-lib-kafka'


pipeline {
    agent {
        label 'whis-bld02'
    }
    
    environment {
        DOCKER_BUILDKIT = 1
    }

    stages {
        stage('Build') {
            steps {
                sh "git clean -dfx"

                script {
                    TAG = sh(returnStdout: true, script: "date --utc +%Y%m%d%H%M%S").trim()
                    BUILD_DATE = sh(returnStdout: true, script: "date --utc +%FT%T.%3NZ").trim()
                    VCS_REF = sh(returnStdout: true, script: "git rev-parse HEAD").trim()
                }

                withCredentials([[$class: 'ZipFileBinding', credentialsId: "WHIDevOps-docker-config", variable: 'DOCKER_CONFIG']]) {
                    script {
                        buildUtilImage = docker.image("${DOCKER_REGISTRY}/${BUILD_UTIL_IMAGE}")
                        buildUtilImage.pull()
                        buildUtilImage.inside {
                            sh "export PIP_INDEX_URL=https://${USERNAME}:${PASSWORD}@na.artifactory.swg-devops.com/artifactory/api/pypi/wh-imaging-pypi-local/simple"
                            sh "./gradlew clean build coverage"
                        }
                    }
                }
            }
        }

        stage('SonarQube') {
            steps {
                withSonarQubeEnv('whi-sonar') {
                    
                    withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'WHIDevOps-jfrog-cred',
                                      usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                        script{
                            if (env.BRANCH_NAME == MAINLINE_BRANCH) {
                                // Mainline
                                withCredentials([[$class: 'ZipFileBinding', credentialsId: "WHIDevOps-docker-config", variable: 'DOCKER_CONFIG']]) {
                                    script {
                                        buildUtilImage = docker.image("${DOCKER_REGISTRY}/${BUILD_UTIL_IMAGE}")
                                        buildUtilImage.pull()
                                        buildUtilImage.inside {
                                            sh "./gradlew -PtaasArtifactoryUsername=$USERNAME -PtaasArtifactoryPassword=$PASSWORD -Dsonar.github.disableInlineComments=true --info --refresh-dependencies sonarqube"
                                        }
                                    }
                                }
                            }
                            else if (env.CHANGE_ID != null && env.CHANGE_ID != "") {
                                // PR
                                withCredentials([[$class: 'ZipFileBinding', credentialsId: "WHIDevOps-docker-config", variable: 'DOCKER_CONFIG']]) {
                                    script {
                                        buildUtilImage = docker.image("${DOCKER_REGISTRY}/${BUILD_UTIL_IMAGE}")
                                        buildUtilImage.pull()
                                        buildUtilImage.inside {
                                            sh "./gradlew -PtaasArtifactoryUsername=${USERNAME} -PtaasArtifactoryPassword=${PASSWORD} -Dsonar.github.disableInlineComments=true -Dsonar.pullrequest.github.repository=${GIT_REPO} -Dsonar.pullrequest.branch=${env.BRANCH_NAME} -Dsonar.pullrequest.key=${env.CHANGE_ID} -Dsonar.pullrequest.base=${env.CHANGE_TARGET} --info sonarqube"
                                        }
                                    }
                                }
                            }
                            else
                            {
                                // Branch
                                echo "Branch analysis disabled for SonarQube"
                            }
                        }
                    }
                }
            }
        }

        stage('Publish') {
            when {
                branch 'master'
            }

            steps {
                echo 'Publishing....'

                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'WHIDevOps-jfrog-cred',
                                      usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {
                    withCredentials([[$class: 'ZipFileBinding', credentialsId: "WHIDevOps-docker-config", variable: 'DOCKER_CONFIG']]) {
                        script {
                            buildUtilImage = docker.image("${DOCKER_REGISTRY}/${BUILD_UTIL_IMAGE}")
                            buildUtilImage.pull()
                            buildUtilImage.inside {
                                sh "./gradlew -PtaasArtifactoryUsername=$USERNAME -PtaasArtifactoryPassword=$PASSWORD uploadArchives"
                            }
                        }
                        
                    }
                }
                
            }
        }
        stage('Copyright Check') {
    		steps {
    			copyCheck failOnError: false
    		}
		}        
    }

    post {
        always {
            whiNotify(SLACK_CHANNEL, NOTIFY_PR_IN_SLACK)
        }
    }
}
