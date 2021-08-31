library 'jenkins-shared-library@master'
import groovy.json.*

pipeline {
	agent none
	options {
		timeout( time: 2, unit: 'HOURS' )
	}
	stages {
		stage('Db2 Data Gate CLI FYRE/OCP+ end-to-end test') {
			agent {
				kubernetes {
					cloud 'icp-production'
					customWorkspace '/home/dwabuild/workspace'
					slaveConnectTimeout '300'
					yaml libraryResource('podspecs/centoscppbuild-latest-small-x86.yml')
				}
			}
			environment {
				IBM_GITHUB_PERSONAL_ACCESS_TOKEN = credentials("dwabuild-ghe-repo")
				FYRE_API_KEY = credentials('idaafyreicp-fyre-api-key')
				FYRE_API_USER_NAME = "idaa.fyreicp"
			}
			steps {
				script {
					echo "Running Db2 Data Gate CLI FYRE/OCP+ end-to-end test"
					sh "tests/test_fyre/test.sh"
				}
			}
		}
	}
}
