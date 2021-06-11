library 'jenkins-shared-library@master'
import groovy.json.*

pipeline {
	agent none
	options {
		timeout( time: 2, unit: 'HOURS' )
	}
	stages {
		stage('Data Gate CLI FYRE/OCP+ end-to-end test') {
			agent {
				kubernetes {
					cloud 'icp-production'
					customWorkspace '/home/dwabuild/workspace'
					slaveConnectTimeout '300'
					yaml libraryResource('podspecs/centoscppbuild-latest-small-x86.yml')
				}
			}
			environment {
				FYRE_API_KEY = credentials('idaafyreicp-fyre-api-key')
				FYRE_API_USER_NAME = "idaa.fyreicp"
				GITHUB_API_KEY = credentials("dwabuild-ghe-repo")
			}
			steps {
				script {
					echo "Running Data Gate CLI FYRE/OCP+ end-to-end test"
					sh "tests/test_fyre/test.sh"
				}
			}
		}
	}
}
