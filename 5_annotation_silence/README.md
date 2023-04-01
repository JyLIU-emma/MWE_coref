README
------

Ce dossier regroupe les expérience d'annotations manuelles destinées à estimer le silence des 3 outils utilisés dans l'étude du corpus pour l'article JLM ("We thought that the eyes of cereference were shut to multiword expressions and they mostly are").

Silence MWE identification
-------
The silence_Seen2Seen/ folder contains a copy of some files from the ANCOR-OTG corpus, in the .cupt format, annotated automatically for MWEs by the Seen2Seen tool.
We simply manually correct the existing annotations, and then calculate this gold version to the automatically annotated version.
The rationale is the following:
* Seen2Seen is trained on the PARSEME corpus, which, for French, contains written texts (national and regional newswire, Wikipedia, drug notices).
* Then Seen2Seen is used to automatically identify MWEs in transcribed speech
* The objective is to corroborate the hypothesis that internal components of MWEs should not occur in non-trivial coreference chains.
* If the silence of Seen2Seen on out-of-domain (speech) texts is too high, the corroboration of the hypothesis is not reliable enough.
* Therefore we estimate efficiency of Seen2Seen on out-of-domain texts by manually correcting a sample of such text
* We select ANCOR OTG subcorpus, since this is the most spontaneous-speech genre within ANCOR 
* We select also one ANCOR-CO2-ESLO interview to have more diverse contents

Observations:
* Results:
  `MWE-based: P=150/181=0.8287 R=150/259=0.5792 F=0.6818`
  `Tok-based: P=382/437=0.8741 R=382/644=0.5932 F=0.7068`
* The missed VMWE annotations which should have been anotated as true:
  * /j' ai **eu** un <ins>**accident**</ins> qui aurait pu être un accident grave et c'est-à-dire que j' ai **fait** <ins>un **saut** de six mètres en contrebas de la Nationale vingt</ins>/
  * /est -ce que vous **avez** des <ins>**préférences**</ins> côté papier ? bah j' ai- n- j' **ai <ins>horreur</ins>** des papiers de mauvaises qualité
  * /mon père est a dû **poursuivre** des <ins>**études**</ins> jusque il était licencié en droit euh il a du **poursuivre** ses <ins>**études**</ins> jusque je ne sais pas oui trois ans
  * /pendant l' évacuation j' ai été <ins>un trimestre à l' école euh laïque et obligatoire</ins> et dont j' ai gardé un souvenir euh tout à fait remarquable [...] très positifs par rapport à l' <ins>**enseignement**</ins> dont j' avais de j' avais **bénéficié** et avant et après/
  
  * /mais enfin je crois que <ins>ça</ins> c ' est c ' est de les <ins>**supputations**</ins> qui euh qui ne se **posent** pas hein/
  * /sauf euh lorsque le malade **pose** de les <ins>**exigences**</ins> <ins>qui</ins> ne sont pas les exigences habituelles si vous voulez/
  * /elle a **fait** un **choix** <ins>qui</ins> fait protester un certain nombre de ses consultants/
  * /pour euh revendiquer sur le le **statut** <ins>que</ins> nous pouvons **avoir** vis-à-vis de la Sécurité Sociale/
* A nice literal occurrence: /je voudrais prendre la ligne trente-trois on **n' a pas de prix** non non il y a il y a il y a rien il y a rien/


