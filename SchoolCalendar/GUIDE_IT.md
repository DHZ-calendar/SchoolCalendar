[TOC]

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

![Home Empty](static/readme_pics/home_empty.png)

Apri il menù in alto a sinistra, clicca sul bottone `Gestisci le entità`, apri l'istanza che vuoi inserire (ad esempio `Insegnanti`), e inserisci gli oggetti che ti servono per far funzionare il servizio. Facciamo un breve riepilogo delle entità:

- **Insegnante**: i professori della tua scuola. Ogni insegnante avrà il suo account, così che sia per loro possibile visualizzare il loro orario settimanale. Lo `username` è quello che serve per effettuare il login (ergo, sceglilo attentamente: non ci possono essere spazi). Consigliamo di utilizzare come username `nome_cognome`, ad esempio `dante_alighieri`. Il campo `email` serve per invitare gli insegnanti al sito, e far scegliere loro la password dei loro account (anche se gli insegnanti non hanno accettato l'invito, potrai inserirli nel calendario). Da notare che l'email di invito non viene inviata automaticamente: dovrai cliccare sul bottone menù a sinistra -> `Gestisci le entità` -> `Insegnanti` -> `Manda un invito`.
- **Classe**: ad esempio, classe IA. Il campo `anno` è un numero (non romano), nel caso di esempio 1. Il campo `sezione` invece sarebbe A.
- **Aula**: per avere la massima flessibilità, puoi registrare nel sistema ogni aula della tua scuola. In questo modo, puoi tenere traccia dei conflitti che avvengono nelle aule (ci aspettiamo che la stessa aula non possa essere usata da troppe classi contemporaneamente). Fa' attenzione che il campo `Capacità` si riferisce a quante classi possono stare nell'aula contemporaneamente, e non a quanti studenti possano entrare. Ad esempio, un laboratorio o la palestra possono essere usati da più classi assieme. Ad ogni modo, ci aspettiamo che per la maggior parte delle aule la loro capacità sia 1.
- **Materia**: (matematica, letteratura etc).
- **Vacanze**: non vorrai che studenti e insegnanti lavorino a Natale ;) La vacanza è valida per ogni classe della scuola. Se provi a inserirne una, vedrai che viene colorata di arancione nel calendario.
- **Stage**: come una vacanza (non ci possono essere lezioni nelle giornate di stage), ma è specifico per una singola classe.
- **Slot Orari**: è lo slot orario dove le lezioni possono essere tenute. Ad esempio, assumiamo che il martedì la terza ora duri dalle 11:05 alle 11:55. Allora il campo `Numero di ora` è 3. Inoltre, se nei vari report annuali vuoi contare le ore di lezione come un'ora piena, anche se la durata è soltanto di 50 minuti (come nell'esempio sopra), allora puoi specificarlo nel campo `durata legale`. Purtroppo questo inserimento potrebbe essere un po' faticoso, visto che ci aspettiamo ci siano circa 30 slot orari in una settimana: non ti preoccupare, ti abbiamo risparmiato un sacco di tempo, infatti puoi decidere di replicare gli slot orari nei vari giorni della settimana. Per selezionare più giorni nel form di inserimento, usa i tasti `ctrl` e `shift`. Infine, gli slot orari sono raggruppati per gruppi chiamati `gruppi di slot orari`. Questi gruppi ti consentono di gestire diversi orari per le diverse classi, durante lo stesso anno scolastico (ad esempio, la classe IA inizia la prima ora alle 7:45, mentre la classe IB inizia alle 8:15). Ti basterà creare due gruppi di slot orari, uno con le ore che iniziano alle 7:45, l'altro con le ore che iniziano alle 8:15, e il sistema gestirà automaticamente le collisioni e i problemi. Se, invece, la tua scuola ha gli stessi orari per tutte le classi, allora ti sarà sufficiente un solo gruppo di slot orari per ogni anno scolastico.
- **Blocchi di Assenza**: se qualche insegnante ha qualche indisponibilità cronica ad insegnare in determinate fasce orarie, puoi registrarlo utilizzando i `Blocchi di Assenza`. Quando successivamente verificherai la disponibilità di quell'insegnante ad insegnare in una determinata classe, tale Slot Orario non verrà considerato valido, anche se l'insegnante non ha altri conflitti in quel lasso di tempo.
- **Ore per Insegnante in Classe**: tiene traccia quante ore di insegnamento (campo `Ore`) ogni insegnante deve fare in ogni classe. Considera che quando si calcola la quantità totale di ore svolte da un insegnante in una classe, viene utilizzato il campo `Durata Legale` dell'entità `Sto Orario`. Se un insegnante insegna più materie nella stessa classe (ad esempio fisica e matematica), ha bisogno di più `Ore per Insegnante in Classe` (una per matematic e una per fisica nel caso di esempio). Il campo `Ora BES` è pensato per le ore speciali di insegnamento (come le ore svolte con alunni portatori di disabilità). Se la tua scuola non necessita di queste particolari ore di insegnamento, lascia i campi impostati a zero. Le ore di codocenza sono spiegate nella sezione sottostante.
- **Segretario/a**: i segretari della tua scuola che hanno bisogno di vedere tutti gli orari. Ad esempio, può essere utile se un segretario ha bisogno di inviare una comunicazione urgente ad un insegnante e vuole sapere dove l'insegnante sta attualmente insegnando. I segretari hanno anche la possibilità di scaricare i report excel con gli orari delle classi, dei docenti e delle aule.
- **Carico Annuale per Insegnante**: la quantità totale di ore che un docente dovrebbe insegnare in un anno accademico. Le ore sono suddivise in ore normali, ore B.E.S. e ore di codocenza. *Questa è un'entità facoltativa che può aiutare durante la creazione di un orario: permette di confrontare il numero di ore assegnate a un insegnante e il carico annuale desiderato per quell'insegnante.*
- **Carico Annuale per Classe**: la quantità totale di ore che una classe dovrebbe avere in un anno accademico. Le ore sono suddivise in ore normali e ore B.E.S. *Questa è un'entità facoltativa che può aiutare durante la creazione di un orario: permette di confrontare il numero di ore assegnate a una classe e il carico annuale desiderato per quella classe.*

Compila questi campi con attenzione! Tutte le informazioni che fornisci al sito web devono essere corrette, altrimenti funzionerà (ovviamente) non nel modo desiderato!

### Un esempio di creazione delle entità
Ora che abbiamo eseguito la fase di introduzione, possiamo finalmente iniziare a utilizzare il servizio! In questa sottosezione ti guideremo in questo processo.

Per questo esempio, abbiamo creato un account amministratore scolastico (lo stesso tipo di account che stai utilizzando in questo momento) chiamato John Doe, che è il manager della scuola "Galilei High School". Non puoi creare una scuola nè un nuovo anno scolastico con il tuo account corrente: devi chiedere agli amministratori (le persone che ti hanno creato l'account) del sito web di aggiungere la tua scuola o l'anno scolastico nel sistema!

Ora che abbiamo tutto pronto iniziamo a compilare quanto necessario per utilizzare correttamente il sito: partiamo dalle basi e inseriamo alcuni slot orari. Apri il menù sulla sinistra, clicca su `Gestisci le entità` e seleziona `Slot orari`. Aggiungi un nuovo gruppo di slot orari per l'anno scolastico in corso.

![HourSlotGroupCreate](static/readme_pics/HourSlotGroupInsertion.png)

Ora dovresti vedere un elenco di tutti i tuoi gruppi di slot orari:

![HourSlotsGroupsList](static/readme_pics/HourSlotsGroupsList.png)

Clicca sul pulsante `Modifica blocchi` e aggiungi i singoli blocchi orari (usando il pulsante verde `+ Aggiungi nuovo`).

![HourSlotCreate](static/readme_pics/HourSlotInsertion.png)

(Nota che in questo caso l'ora dura fisicamente solo 50 minuti, ma la durata legale assicura che verrà conteggiata come un'intera ora di lezione da 60 minuti). Inseriamo sia lo slot orario per la prima ora (7.55-8.45) che per la seconda ora (8.45-9.35).

![TimetableWithHourslots](static/readme_pics/timetable_with_hourslots.png)

Inseriamo ora alcune classi (1A, 2A, 3A, 4A, 5A): vai nel menù di sinistra -> `Gestisci le entità` -> `Classi` -> `Aggiungi nuovo`, e compila i moduli con le informazioni delle varie classi (attenzione, se il corso è 1A, l'anno sarà 1 - deve essere un numero - mentre la sezione sarà A). Per esempio:

![CourseCreation](static/readme_pics/Course_creation.png)

Si noti che il campo Gruppo di Slot Orari definisce l'anno scolastico della classe che si sta inserendo: potresti infatti avere un corso 1A sia nell'anno scolastico 2020-2021 che nel 2021-2022, puoi differenziarli semplicemente guardando il Gruppo di Slot Orari a cui sono associati!

Inseriamo ora alcune materie (menù di sinistra -> `Gestisci le entità` -> `Materie` -> `Aggiungi nuovo`): Matematica, Fisica, Letteratura italiana, Letteratura inglese. Il campo Colore viene utilizzato per definire il colore con cui appariranno nell'orario.

Inseriamo ora alcune aule: non è necessario inserirle tutte (anche se non c'è nessuna controindicazione nel farlo), ma solamente quelle che ritieni possano avere conflitti (ad esempio i laboratori che possono essere utilizzati da più classi).

Per aggiungere alcune aule vai nel menù a sinistra -> `Gestisci le entità` -> `Aule` -> `Aggiungi nuovo`. Creiamo un paio di aule, come il Laboratorio di Fisica (con capacità 2, il che significa che può essere utilizzato contemporaneamente da due classi e non che può ospitare solo due studenti) e il Laboratorio Multimediale (con capacità 1).

![RoomCreation](static/readme_pics/rooms_creation.png)

È ora di aggiungere degli insegnanti: vai nel menù a sinistra -> `Gestisci le entità` -> `Insegnanti` -> `Aggiungi nuovo` e crea alcuni insegnanti. Per questo esempio creeremo gli insegnanti Marie Curie, Dante Alighieri, Oscar Wilde e Carl Friedrich Gauss.

Nota che: il campo `username` sarà il nome utente che il docente utilizzaerà per effettuare il login - sceglilo con attenzione perchè non possono esserci duplicati e non può contenere spazi (si consiglia di usare nome_cognome, ad esempio dante_alighieri può essere il nome utente per il docente Dante Alighieri). Il campo email è necessario poichè l'insegnante riceverà un'email da SchoolCalendar, al fine di impostare la sua password (utilizzerà il suo account per controllare il suo orario personale, ma non potrà modificare nulla non essendo un amministratore!). L'email non è inviata automaticamente: è necessario cliccare sul pulsante `Manda un invito` andando nel menù a sinistra della pagina -> `Gestisci le entità` -> `Insegnanti`.

![TeacherCreate](static/readme_pics/teacher_create.png)
