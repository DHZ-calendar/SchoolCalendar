# SchoolCalendar
![Django CI](https://github.com/DHZ-calendar/SchoolCalendar/workflows/Django%20CI/badge.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/dhz-calendar/schoolcalendar/badge)](https://www.codefactor.io/repository/github/dhz-calendar/schoolcalendar)


## Presentazione

Sappiamo quanti sia difficile creare il calendario per una scuola: nessuna classe può essere lasciata senza un insegnante, allo stesso tempo nessun insegnante può essere assegnato a più classi contemporaneamente - a meno che i viaggi nel tempo non siano possibili, ma questa è decisamente un'altra storia ;). E, inoltre, entro la fine dell'anno tutti i professori devono aver compiuto il loro carico orario annuale. E se alcuni insegnanti dovessero essere sostituiti durante l'anno? Un disastro!

Ma non preoccuparti, si dà il caso che ti potremmo aver reso la vita molto più facile: SchoolCalendar è il tool che ti aiuta a generare l'orario per la tua scuola.

Il sito ti aiuta a tenere traccia della disponibilità degli insegnanti, delle classi e delle aule nella tua scuola, così che mentre crei il calendario non ci siano conflitti. Se sei il dirigente della tua scuola (o la persona incaricata di creare l'orario), una pagina interattiva ti permette di generare il calendario; inoltre, tutti gli insegnanti possono vedere il loro orario settimanale loggandosi sul sito sul loro account personale. Inoltre, c'è la possibilità di gestire le supplenze che accadono improvvisamente durante l'anno. E, infine, puoi tenere traccia del carico annuale degli insegnanti e delle classi con dei report annuali.

La prossima sezione ti spiegherà come installare il servizio, e come usarlo.

Voi provarlo? Contattaci: https://schoolcalendar.it/.

Iniziamo!

## Guida Utente

### Inizializzazione

Sei il preside di una scuola e hai appena ottenuto le credenziali del tuo account: ti starai chiedendo cosa tu debba fare.

Per cominciare, apri un browser (sconsigliamo vivamente l'utilizzo di Internet Explorer), inserisci il link al servizio e fai il login con le tue credenziali.

Dovresti vedere una pagina simile a questa:

![Home Empty](readme_pics/home_empty.png)

Apri il menù in alto a sinistra, clicca sul bottone `Gestisci le entità`, apri l'istanza che vuoi inserire (ad esempio `Insegnanti`), e inserisci gli oggetti che ti servono per far funzionare il servizio. Facciamo un breve riepilogo delle entità:

- **Insegnante**: i professori della tua scuola. Ogni insegnante avrà il suo account, così che sia per loro possibile visualizzare il loro orario settimanale. Lo `username` è quello che serve per effettuare il login (ergo, sceglilo attentamente: non ci possono essere spazi). Consigliamo di utilizzare come username `nome_cognome`, ad esempio `dante_alighieri`. Il campo `email` serve per invitare gli insegnanti al sito, e far scegliere loro la password dei loro account (anche se gli insegnanti non hanno accettato l'invito, potrai inserirli nel calendario). Da notare che l'email di invito non viene inviata automaticamente: dovrai cliccare sul bottone menù a sinistra -> Gestisce le entità -> Insegnanti -> Manda un invito.
- **Corso**: ad esempio, classe IA. Il campo `anno` è un numero (non romano), nel caso di esempio 1. Il campo `sezione` invece sarebbe A.
- **Aula**: per avere la massima flessibilità, puoi registrare nel sistema ogni aula della tua scuola. In questo modo, puoi tenere traccia dei conflitti che avvengono nelle aule (ci aspettiamo che la stessa aula non possa essere usata da troppe classi contemporaneamente). Fa' attenzione che il campo `Capacità` si riferisce a quante classi possono stare nell'aula contemporaneamente, e non a quanti studenti possano entrare. Ad esempio, un laboratorio o la palestra possono essere usati da più classi assieme. Ad ogni modo, ci aspettiamo che per la maggior parte delle aule la loro capacità sia 1.
- **Materia**: (matematica, letteratura etc).
- **Vacanze**: non vorrai che studenti e insegnanti lavorino a Natale ;) La vacanza è valida per ogni classe della scuola. Se provi a inserirne una, vedrai che viene colorata di arancione nel calendario.
- **Stage**: come una vacanza (non ci possono essere lezioni nelle giornate di stage), ma è specifico per una singola classe.
- **Slot Orari**: è lo slot orario dove le lezioni possono essere tenute. Ad esempio, assumiamo che il martedì la terza ora duri dalle 11:05 alle 11:55. Allora il campo `Numero di ora` è 3. Inoltre, se nei vari report annuali vuoi contare le ore di lezione come un'ora piena, anche se la durata è soltanto di 50 minuti (come nell'esempio sopra), allora puoi specificarlo nel campo `durata legale`. Purtroppo questo inserimento potrebbe essere un po' faticoso, visto che ci aspettiamo ci siano circa 30 slot orari in una settimana: non ti preoccupare, ti abbiamo risparmiato un sacco di tempo, infatti puoi decidere di replicare gli slot orari nei vari giorni della settimana. Per selezionare più giorni nel form di inserimento, usa i tasti `ctrl` e `shift`. Infine, gli slot orari sono raggruppati per gruppi chiamati `gruppi di slot orari`. Questi gruppi ti consentono di gestire diversi orari per le diverse classi, durante lo stesso anno scolastico (ad esempio, la classe IA inizia la prima ora alle 7:45, mentre la classe IB inizia alle 8:15). Ti basterà creare due gruppi di slot orari, uno con le ore che iniziano alle 7:45, l'altro con le ore che iniziano alle 8:15, e il sistema gestirà automaticamente le collisioni e i problemi. Se, invece, la tua scuola ha gli stessi orari per tutte le classi, allora ti sarà sufficiente un solo gruppo di slot orari per ogni anno scolastico.
- 


