exports.config = {
    specs: ['./test/spec/**/*.js'],
    maxInstance:10,
    capabilities:[{
        maxInstances: 5,
        browserName: 'firefox',
        marionette: true,
        javascriptEnabled: true,
        acceptSslCerts: true,
        acceptInsecureCerts: true
    }],
    sync: true,
    logLevel: 'silent',
    coloredLogs: true,
    deprecationWarnings: true,
    bail: 0,
    screenshotPath: './test/errorShots/',
    baseUrl: 'https://localhost:9090',
    waitforTimeout: 10000,
    connectionRetryTimeout: 90000,
    connectionRetryCount: 3,
    services: ['selenium-standalone'],
    framework: 'jasmine',
    seleniumLogs: './test/logs/',
    reporters: ['spec'],
    jasmineNodeOpts: {
        defaultTimeoutInterval: 10000,
        expectationResultHandler: function(passed, assertion) {
            /**
             * only take screenshot if assertion failed
             */
            if(passed) {
                return;
            }

            browser.saveScreenshot('assertionError_' + assertion.error.message + '.png');
        }
    }
}
