/*******************************************************************************
 * IBM Watson Imaging Common Application Framework 3.0                         *
 *                                                                             *
 * IBM Confidential                                                            *
 *                                                                             *
 * OCO Source Materials                                                        *
 *                                                                             *
 * (C) Copyright IBM Corp. 2019                                                *
 *                                                                             *
 * The source code for this program is not published or otherwise              *
 * divested of its trade secrets, irrespective of what has been                *
 * deposited with the U.S. Copyright Office.                                   *
 *******************************************************************************/
 
String DOCKER_REGISTRY="wh-imaging-dev-docker-local.artifactory.swg-devops.com"
String BUILD_UTIL_IMAGE="whi-image-python37-build-util:latest"
String VERSION="3.0.0"
String SLACK_CHANNEL="#whi-caf-builds"
boolean NOTIFY_PR_IN_SLACK=true
String MAINLINE_BRANCH="master"
String GIT_REPO='WH-Imaging/whi-caf-lib-kafka'
String PROJECT_NAME="whi-caf-lib-kafka"
String APPSCAN_APP_ID="e6df4e91-77a9-4d34-a554-e87663f1b299"

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
                slackSend color: "#00cc00", channel: SLACK_CHANNEL, teamDomain: 'ibm-watsonhealth', tokenCredentialId: 'ibm-watsonhealth_slack_token', message: "Build Started: ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"

                sh "git clean -dfx"

                script {
                    TAG = sh(returnStdout: true, script: "date --utc +%Y%m%d%H%M%S").trim()
                    BUILD_DATE = sh(returnStdout: true, script: "date --utc +%FT%T.%3NZ").trim()
                    VCS_REF = sh(returnStdout: true, script: "git rev-parse HEAD").trim()
                }

                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'WHIDevOps-jfrog-cred',
                                    usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD']]) {

                    withCredentials([[$class: 'ZipFileBinding', credentialsId: "WHIDevOps-docker-config", variable: 'DOCKER_CONFIG']]) {
                        script {
                            buildUtilImage = docker.image("${DOCKER_REGISTRY}/${BUILD_UTIL_IMAGE}")
                            buildUtilImage.pull()
                            buildUtilImage.inside {
                                sh "export PIP_EXTRA_INDEX_URL=https://${USERNAME}:${PASSWORD}@na.artifactory.swg-devops.com/artifactory/api/pypi/wh-imaging-pypi-local/simple; ./gradlew clean build coverage"
                            }
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

        stage('AppScan') {
            when {
                expression {
                return "${BRANCH_NAME}" == "master" || "${BRANCH_NAME}" =~ /^release-/
                }
            }
            steps {
                    appscan application: "${APPSCAN_APP_ID}", credentials: 'WHI_ASOC_C3CVMJYH_FUNCTIONAL_CRED', name: "${PROJECT_NAME}-${env.BUILD_ID}", scanner: static_analyzer(hasOptions: true, target: "${env.WORKSPACE}/src/main/py"), type: 'Static Analyzer'
            }
        }

        stage('Publish') {
            when {
                expression {
                return "${BRANCH_NAME}" == "master" || "${BRANCH_NAME}" =~ /^release-/
                }
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
            when {
                expression {
                return "${BRANCH_NAME}" == "master" || "${BRANCH_NAME}" =~ /^release-/
                }
            }            
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
