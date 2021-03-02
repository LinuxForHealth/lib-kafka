/*******************************************************************************
* IBM Watson Imaging Common Application Framework 3.2                         *
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
    imageVersion = "3.2.0"

    buildUtilImageRepo = "wh-imaging-dev-docker-local.artifactory.swg-devops.com"
    buildUtilImage = "ubi8/whi-image-ubi8-advisor-p38-builder:latest"

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

    enablePublishArtifact = true
    enablePublishWheel = true

    enableWickedScan = true
    wickedScanDir = 'src/main/py'
    wickedFailOnError = false

    enableCopyCheck = true
    copyCheckFailOnError = false

    slackNotifyChannel = "#whi-caf-builds"
    slackNotifySuccess = true
    slackNotifyPR = true
    slackNotifyPRSuccess = true
    slackNotifyAtChannelOnError = false
}
