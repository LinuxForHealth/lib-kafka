/*******************************************************************************
* IBM Watson Imaging Common Application Framework 3.1                         *
*                                                                             *
* IBM Confidential                                                            *
*                                                                             *
* OCO Source Materials                                                        *
*                                                                             *
*  Copyright IBM Corporation 2019, 2020                                       *
*                                                                             *
* The source code for this program is not published or otherwise              *
* divested of its trade secrets, irrespective of what has been                *
* deposited with the U.S. Copyright Office.                                   *
*******************************************************************************/

whiBuild {
    buildType = "DEFAULT"

    imageName = "whi-caf-lib-kafka"
    imageVersion = "3.1.0"

    buildUtilImageRepo = "wh-imaging-dev-docker-local.artifactory.swg-devops.com"
    buildUtilImage = "ubi8/whi-image-ubi8-python38-builder:latest"

    enableDockerBuild = false

    enableGradleBuild = true
    gradleExtraParams = "coverage"

    enableSonarQube = true
    waitForSonarQubeQualityGate = false

    enableAppScan = true
    appScanAppId = "d17068aa-19d5-430e-bd4d-76637a0b4f0b"
    appScanTarget = { config ->
        return "${this.env.WORKSPACE}/src/main/py"
    }


    enableWickedScan = true
    wickedScanDir = 'src/main/py'
    wickedFailOnError = false

    enableCopyCheck = true
    copyCheckFailOnError = false

    postBuild = { config ->
        println "Publishing wheel"
        withCredentials([usernamePassword(credentialsId: "${config.mavenRepoCredentialId}", passwordVariable: "PASSWORD", usernameVariable: "USERNAME")]) {
            if(config.isStandardBranch) {
                script{
                    refreshOpt = config.gradleNoDependencyRefresh ? "" : "--refresh-dependencies"
                    buildUtilImage = this.docker.image("${config.buildUtilImageRepo}/${config.buildUtilImage}")
                    buildUtilImage.pull()
                    buildUtilImage.inside {
                        sh "fix-repo-credentials.sh"
                        sh "gradle --info $refreshOpt uploadArchives"
                        sh "delete-repo-credentials.sh"
                    }
                }
            }
        }
    }

    slackNotifyChannel = "#whi-caf-builds"
    slackNotifySuccess = true
    slackNotifyPR = true
    slackNotifyPRSuccess = true
    slackNotifyAtChannelOnError = false
}