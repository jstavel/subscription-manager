import LoginPage from '../pageobjects/login.page';
import MainPage from '../pageobjects/main.page';
import RegisterDialog from '../pageobjects/register.dialog';
const env = require('env2')('.env');

describe('Proxy Dialog', function () {
    it('should save values in a file /etc/rhsm/rhsm.conf', function () {
        LoginPage.open();
        LoginPage.wait();
        LoginPage.login(process.env.COCKPIT_USER_NAME,
                        process.env.COCKPIT_USER_PASSWORD)
    })
})
