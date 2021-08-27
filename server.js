const express = require('express');
const serveIndex = require('serve-index');
const app = express();

app.get('/', function(req, res) {
    res.send(`Current endpoints:<br>/paknsave<br>/newworld<br>/countdown<br>/thewarehouse<br>/freshchoice<br>/supervalue<br>/mightyape<br>/data_changes<br><br>Example usage: GET /paknsave/latest.json<br>Returns: JSON price data`)
})
app.use('/paknsave', express.static(__dirname + '/data/paknsave'), serveIndex(__dirname + '/data/paknsave'))
app.use('/newworld', express.static(__dirname + '/data/newworld'), serveIndex(__dirname + '/data/newworld'))
app.use('/countdown', express.static(__dirname + '/data/countdown'), serveIndex(__dirname + '/data/countdown'))
app.use('/thewarehouse', express.static(__dirname + '/data/thewarehouse'), serveIndex(__dirname + '/data/thewarehouse'))
app.use('/freshchoice', express.static(__dirname + '/data/freshchoice'), serveIndex(__dirname + '/data/freshchoice'))
app.use('/supervalue', express.static(__dirname + '/data/supervalue'), serveIndex(__dirname + '/data/supervalue'))
app.use('/mightyape', express.static(__dirname + '/data/mightyape'), serveIndex(__dirname + '/data/mightyape'))
app.use('/data_changes', express.static(__dirname + '/data_changes'), serveIndex(__dirname + '/data_changes'))
app.use('/static', express.static(__dirname + '/public'))

app.listen(8880, () => {
    console.log('Listening')
})