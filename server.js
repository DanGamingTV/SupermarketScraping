const express = require('express');
const serveIndex = require('serve-index');
const app = express();

app.get('/', function(req, res) {
    res.send(`Current endpoints:<br>/paknsave<br>/newworld<br>/countdown<br>/thewarehouse<br>/freshchoice<br>/supervalue<br><br>Example usage: GET /paknsave/latest.json<br>Returns: JSON price data`)
})
app.use('/paknsave', express.static(__dirname + '/Paknsave/data'), serveIndex(__dirname + '/Paknsave/data'))
app.use('/newworld', express.static(__dirname + '/NewWorld/data'), serveIndex(__dirname + '/NewWorld/data'))
app.use('/countdown', express.static(__dirname + '/Countdown/data'), serveIndex(__dirname + '/Countdown/data'))
app.use('/thewarehouse', express.static(__dirname + '/TheWarehouse/data'), serveIndex(__dirname + '/TheWarehouse/data'))
app.use('/freshchoice', express.static(__dirname + '/FreshChoice/data'), serveIndex(__dirname + '/FreshChoice/data'))
app.use('/supervalue', express.static(__dirname + '/SuperValue/data'), serveIndex(__dirname + '/SuperValue/data'))

app.listen(3000, () => {
    console.log('Listening')
})