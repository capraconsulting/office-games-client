**For å registrere seg:**

Bli med i #kontorspill på Slack og les av kortet på leseren. Kortleseren er plassert under bordet, ved nettet mot glassveggen.

Det blir da postet en melding til Slack kanalen:

> Ukjent kort prøvde å spille: xxxxxxx

Bruk kommandoen `/kontor_spill_registrer xxxxxxx` for å begynne registreringen av kortet ditt.

Du får da en melding tilbake (evt. bare prøv igjen, Slash kommandoer har en timeout på 3 sekunder):

> "Kort registrert! Les av kortet ditt på nærmeste spill-kortleser innen 1 time for å fullføre registreringen av kortet."

Når du leser av kortet neste gang så vil kortet bli registrert til din bruker og du får både en konfirmasjon fra @slackbot:

> Et nytt kort har blitt registrert til din bruker: xxxxxxx

men det blir også postet i #kontorspill kanalen:

> @mko has registrert et nytt kort: xxxxxxx

**For å spille:**
* 2 spillere med registrerte kort leser av kortene på leseren, det blir postet info til Slack kanalen om hvem og om spillet har startet.
* Vinneren leser av kortet sitt etter spillet av ferdig (det er en buffer på 1 minutt før man kan registrere en vinner).
* Informasjon om hvem som vant og spillerenes nye rating blir postet til Slack kanalen.

**Litt teknisk:**
* En RPi 3 (med et resin.io image) bruker Python, hidapi, Firebase, Slack API og Slack Slash commands til å sammenkjøre alt.
* Alle starter med 1200 i rating, videre så gjelder ELO rating systemet.
* TV-en inne på bordtennis rommet vil i fremtiden slå seg på automatisk og vise hvem som spiller.
* En webside med historikk, topp 10 o.l. kommer senere.
* Den registrer per i dag bare hvem som vinner, ikke antall poeng per spiller (kommer også senere).