const async = require('asyncawait/async');
const await = require('asyncawait/await');
const functions = require('firebase-functions');
const admin = require('firebase-admin');

admin.initializeApp(functions.config().firebase);

exports.registerCard = functions.https.onRequest(async((request, response) => {
    if (request.method !== "POST") {
        console.error(`Got unsupported ${request.method} request. Expected POST.`);
        return response.send(405, "Only POST requests are accepted");
    }

    if (request.body.token !== functions.config().slack.token) {
        return response.send(401, "Invalid request token!");
    }

    request.body.timestamp = admin.database.ServerValue.TIMESTAMP;

    // Handle the commands later, Slack expect this request to return within 3000ms
    await(admin.database().ref(`pending_registrations/${request.body.text}`).set(request.body));

    return response.contentType("json").status(200).send({
        "response_type": "ephemeral",
        "text": "Kort registrert! Les av kortet ditt på nærmeste spill-kortleser innen 1 time for å fullføre registreringen av kortet."
    });
}));
