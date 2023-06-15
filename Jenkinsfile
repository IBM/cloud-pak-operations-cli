pipeline {
	agent {
		label 'cloud-pak-operations-cli-agent-jnlp'
	}
	stages {
		stage('IBM Cloud Pak Operations CLI Fyre/OCP+ end-to-end test') {
			environment {
				FYRE_CREDENTIALS = credentials('FYRE')
				FYRE_API_KEY = "${FYRE_CREDENTIALS_PSW}"
				FYRE_API_USER_NAME = "${FYRE_CREDENTIALS_USR}"
			}
			steps {
				sh "tests/test_fyre/test.sh"
			}
		}
	}
}
