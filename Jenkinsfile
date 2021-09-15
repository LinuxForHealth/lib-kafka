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

    imageName = "whpa-lib-kafka"
    imageVersion = "1.0.0"

    buildUtilImageRepo = "wh-imaging-cdp-docker-local.artifactory.swg-devops.com"
    buildUtilImage = "ubi8/whpa-cdp-ubi8-builder-python-39x:latest"

    enableDockerBuild = false

    enableGradleBuild = true
    enableHardenedBuild = true
    gradleExtraParams = 'coverage'

    enableSonarQube = true
    waitForSonarQubeQualityGate = false

    enableAppScan = true
    appScanAppId = '7b04262e-2443-40d5-8851-ab5e90eabce8'
    appScanTarget = { config ->
        return "${this.env.WORKSPACE}/src/"
    }

    enablePublishArtifact = true
    enablePublishWheel = true

    enableWickedScan = true
    wickedScanDir = '.'
    wickedFailOnError = false

    // enableCopyCheck = true
    // copyCheckFailOnError = false

    slackNotifyChannel = '#whpa-cdp-builds'
    slackNotifySuccess = true
    slackNotifyPR = true
    slackNotifyPRSuccess = true
    slackNotifyAtChannelOnError = true
}