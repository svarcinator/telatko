soubor ltl_data byl vygenerovan prikazem randltl -n4000 5 --output=ltl_data
- tyto ltl formule budou prelozeny rabinizerem4, ltl3tela a spotem(ltl2tgba)

set3.hoa automaty generovane prikazem ltl2tgba -G -H -D --file=ltl_data --output=set3.hoa
- byly z tama vyfiltrovany automaty s akc. podm delky 1 prikazem:
autfilt --acc-sets=2.. --file=set3.hoa --output=set3.hoa_filtered
- to vyfiltrovany je set3.hoa

vytvoren soubor set3.stats prikazem: 
autfilt --stats='%a %C %F %G' --file=set3.hoa --output=set3.stats
(pocet akc mnozin, pocet scc, jmeno souboru ze ktereho jsou, akc podminka )


set1.hoa - soubor ltl_data prelozen prikazem:
./bin/ltl2dra -I "input" -O "set1.hoa"
a pak analogicky set1.stats


nejde mi to prelozit ltl3tela - vyzaduje c++17
