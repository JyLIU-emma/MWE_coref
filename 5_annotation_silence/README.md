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
  * MWE-based: P=150/181=0.8287 R=150/259=0.5792 F=0.6818
  * Tok-based: P=382/437=0.8741 R=382/644=0.5932 F=0.7068
  * IRV: MWE-proportion: gold=26/259=10% pred=19/181=10%
  * IRV: MWE-based: P=15/19=0.7895 R=15/26=0.5769 F=0.6667
  * IRV: Tok-based: P=30/38=0.7895 R=30/53=0.5660 F=0.6593
  * LVC.cause: MWE-proportion: gold=1/259=0% pred=0/181=0%
  * LVC.cause: MWE-based: P=0/0=0.0000 R=0/1=0.0000 F=0.0000
  * LVC.cause: Tok-based: P=0/0=0.0000 R=0/4=0.0000 F=0.0000
  * LVC.full: MWE-proportion: gold=58/259=22% pred=30/181=17%
  * LVC.full: MWE-based: P=21/30=0.7000 R=21/58=0.3621 F=0.4773
  * LVC.full: Tok-based: P=43/60=0.7167 R=43/117=0.3675 F=0.4859
  * VID: MWE-proportion: gold=174/259=67% pred=132/181=73%
  * VID: MWE-based: P=114/132=0.8636 R=114/174=0.6552 F=0.7451
  * VID: Tok-based: P=307/339=0.9056 R=307/470=0.6532 F=0.7590

* The missed VMWE annotations which should have been anotated as true:
  * _j' ai **eu** <ins>un **accident**</ins> <ins>qui</ins> aurait pu être <ins>un accident grave</ins>_
  * _mais enfin je crois que ça c ' est c ' est de <ins>les **supputations**</ins> <ins>qui</ins> euh <ins>qui</ins> ne se **posent** pas hein_
  * _sauf euh lorsque le malade **pose** de <ins>les **exigences**</ins> <ins>qui</ins> ne sont pas les exigences habituelles si vous voulez_
  * _elle a **fait** <ins>un **choix**</ins> <ins>qui</ins> fait protester un certain nombre de ses consultants_
  * _pour euh revendiquer sur <ins>le le **statut**</ins> <ins>que</ins> nous pouvons **avoir** vis-à-vis de la Sécurité Sociale_
* The missed VMWE annotations which should have been anotated as repeated:
  * _mon père est a dû **poursuivre** <ins>des **études**</ins> jusque il était licencié en droit euh il a du **poursuivre** <ins>ses **études**</ins> jusque je ne sais pas oui trois ans_
* Annotations with a possible non-trivial chain, but not annotated as such in ANCOR:
  * _est -ce que vous **avez** <ins>des **préférences**</ins> côté papier ? bah j' ai- n- j' **ai <ins>horreur</ins>** des papiers de mauvaises qualité_
  * _pendant l' évacuation j' ai été <ins>un trimestre à l' école euh laïque et obligatoire</ins> et dont j' ai gardé un souvenir euh tout à fait remarquable [...] très positifs par rapport à <ins>l' **enseignement**</ins> dont j' avais de j' avais **bénéficié** et avant et après_
* A nice literal occurrence: _je voudrais prendre la ligne trente-trois on **n' a pas de prix** non non il y a il y a il y a rien il y a rien_


