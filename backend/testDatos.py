import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import User, Categoria, Rango, Competencia
from exams.models import TipoPregunta
from django.utils import timezone
from django.db import transaction

# ─── DATOS DE TIPOS DE PREGUNTA ──────────────────────────────────────────────
tipos_pregunta_data = [
    {"tip_pre_cod": 1, "tip_pre_nom": "Selección Multiple"},
    {"tip_pre_cod": 2, "tip_pre_nom": "Pregunta Abierta"},
    {"tip_pre_cod": 3, "tip_pre_nom": "Relacionar Columnas"},
    {"tip_pre_cod": 4, "tip_pre_nom": "Verdadero o Falso"},
]

# ─── DATOS DE CATEGORIAS ──────────────────────────────────────────────────────
categorias_data = [
    {"cat_cod": "0", "cat_nom": "ANALISTA EN FORMACIÓN"},
    {"cat_cod": "1", "cat_nom": "ANALISTA DE CREDITOS JUNIOR"},
    {"cat_cod": "2", "cat_nom": "ANALISTA DE CREDITOS AVANZADO"},
    {"cat_cod": "3", "cat_nom": "ANALISTA DE CREDITOS AVANZADO EXPERTO"},
    {"cat_cod": "4", "cat_nom": "ANALISTA DE CREDITOS AVANZADO SUPERIOR"},
    {"cat_cod": "5", "cat_nom": "ANALISTA DE CREDITOS EXPERTO"},
    {"cat_cod": "6", "cat_nom": "ANALISTA DE CREDITOS SUPERIOR"},
    {"cat_cod": "7", "cat_nom": "ANALISTA SENIOR DE CREDITOS"},
    {"cat_cod": "8", "cat_nom": "ANALISTA SENIOR EXPERTO"},
    {"cat_cod": "9", "cat_nom": "ANALISTA MASTER"},
    {"cat_cod": "99", "cat_nom": "GERENTE DE AGENCIA"},
]

# ─── DATOS DE COMPETENCIAS ───────────────────────────────────────────────────
competencias_data = [
    {"com_cod": "COMP-AGILIDAD-MENTAL", "com_nom": "Agilidad mental / rapidez cognitiva"},
    {"com_cod": "COMP-RAZONAMIENTO-NUMERICO", "com_nom": "Razonamiento numérico"},
    {"com_cod": "COMP-RAZONAMIENTO-FINANCIERO", "com_nom": "Razonamiento financiero"},
    {"com_cod": "COMP-PENSAMIENTO-LOGICO", "com_nom": "Pensamiento lógico"},
    {"com_cod": "COMP-CALCULO-NUMERICO", "com_nom": "Análisis y cálculo numérico"},
    {"com_cod": "COMP-CAPACIDAD-ANALITICA", "com_nom": "Capacidad analítica / pensamiento crítico"},
    {"com_cod": "COMP-PENSAMIENTO-DIGITAL", "com_nom": "Pensamiento y resolución de problemas en entornos digitales"},
    {"com_cod": "COMP-ADAPTABILIDAD-DIGITAL", "com_nom": "Adaptabilidad y disposición al uso de herramientas digitales"},
    {"com_cod": "COMP-TENDENCIAS-CONDUCTUALES", "com_nom": "Tendencias conductuales en el entorno laboral"},
    {"com_cod": "COMP-LIDERAZGO-INFLUENCIA", "com_nom": "Liderazgo e influencia"},
    {"com_cod": "COMP-ESTILO-LIDERAZGO", "com_nom": "Estilo de liderazgo"},
    {"com_cod": "COMP-CULTURA-PREVENTIVA", "com_nom": "Cultura preventiva y gestión del riesgo"},
]

# ─── DATOS DE RANGOS (SANTI GAMEPLAY) ───────────────────────────────────────
rangos_data = [
    {"ran_sig": 1, "ran_nom": "Bronce", "ran_pun_min": 0, "ran_pun_max": 599},
    {"ran_sig": 2, "ran_nom": "Plata", "ran_pun_min": 600, "ran_pun_max": 1499},
    {"ran_sig": 3, "ran_nom": "Oro", "ran_pun_min": 1500, "ran_pun_max": 3499},
    {"ran_sig": 4, "ran_nom": "Platino", "ran_pun_min": 3500, "ran_pun_max": 7999},
    {"ran_sig": 5, "ran_nom": "Diamante", "ran_pun_min": 8000, "ran_pun_max": 999999},
]

users_data = [
    {
        "usu_cod": "PEOPLEADMIN",
        "usu_nom": "ADMINISTRADOR SANTI",
        "usu_dni": "admin123",
        "is_staff": True,
        "cat_cod": "99",
    },
    {
        "usu_cod": "testuser",
        "usu_nom": "Usuario de Prueba",
        "usu_dni": "12345678",
        "is_staff": False,
    },
    {"usu_cod": "46718697","usu_nom": "FLOR DE ROSA MAGAÑO BERNAL","usu_dni": "46718697","usu_tel": "978612471","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73371305","usu_nom": "YULISSA MILAGROS PINTO GAMARRA","usu_dni": "73371305","usu_tel": "946774040","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "45964170","usu_nom": "THALIA YAMILY VALDIVIA BELLO","usu_dni": "45964170","usu_tel": "980738853","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76175307","usu_nom": "ROSA DEL PILAR SAJAMI AGUILAR","usu_dni": "76175307","usu_tel": "983036461","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72219972","usu_nom": "RICARDO SANTIAGO CCOYCA LEON","usu_dni": "72219972","usu_tel": "965302799","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76745882","usu_nom": "ROXANA KAREN SULLCARANI HALANOCCA","usu_dni": "76745882","usu_tel": "901678898","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "47182554","usu_nom": "KAREN HIMELDA CHALLCO PACO","usu_dni": "47182554","usu_tel": "953888818","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71805356","usu_nom": "MERY ELIANA GUTIERREZ AMAO","usu_dni": "71805356","usu_tel": "993355380","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70331116","usu_nom": "HERBERT LEON MACEDO","usu_dni": "70331116","usu_tel": "943173307","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73466474","usu_nom": "TANIA LUISA CRUZ HUANCA","usu_dni": "73466474","usu_tel": "927435639","usu_zon": "SUR","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "60426772","usu_nom": "LUIS FERNANDO VALDIVIA ROJAS","usu_dni": "60426772","usu_tel": "910924795","usu_zon": "SUR","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72393115","usu_nom": "ERICK OSCAR MENDOZA ESCOBAR","usu_dni": "72393115","usu_tel": "957024475","usu_zon": "SUR","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "47981560","usu_nom": "MARISOL CHOQUE HUARICALLO","usu_dni": "47981560","usu_tel": "947353732","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72720134","usu_nom": "JAIRO JORGE QUISPE BEJAR","usu_dni": "72720134","usu_tel": "945947906","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "44084892","usu_nom": "JACQUELINE ZUÑIGA CHAMA","usu_dni": "44084892","usu_tel": "949092139","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75522784","usu_nom": "VALERI CAROLINA FERNANDEZ SUCA","usu_dni": "75522784","usu_tel": "973592757","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72907331","usu_nom": "JUAN DIEGO GUTIERREZ GUTIERREZ","usu_dni": "72907331","usu_tel": "959476882","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72387252","usu_nom": "MARYORET PECRIS LLANOS VILCA","usu_dni": "72387252","usu_tel": "945312835","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72265715","usu_nom": "FRANKLIN HUARACHA MAQUE","usu_dni": "72265715","usu_tel": "918065067","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76597252","usu_nom": "ARNIE VILLAR SIFUENTES","usu_dni": "76597252","usu_tel": "941225457","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75051429","usu_nom": "RUBEN ROLANDO LAGOS CLEMENTE","usu_dni": "75051429","usu_tel": "940117618","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70320225","usu_nom": "JHIMMY JHAEL FERNANDEZ GARCIA","usu_dni": "70320225","usu_tel": "997208124","usu_zon": "CENTRO","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72907503","usu_nom": "CHRISTIAN ALEXIS GUTIERREZ CONDORI","usu_dni": "72907503","usu_tel": "962329637","usu_zon": "CENTRO","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73799879","usu_nom": "ESTEFANY GLADYS QUISPE HUAMAN","usu_dni": "73799879","usu_tel": "992519015","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76651583","usu_nom": "NOVAR AGUSTO DAVILA PERALES","usu_dni": "76651583","usu_tel": "937471532","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76733280","usu_nom": "MARIA DE LOS ANGELES AGUIRRE MIÑOPE","usu_dni": "76733280","usu_tel": "946946801","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "47128198","usu_nom": "VICTOR MIGUEL VILCHEZ PIEDRA","usu_dni": "47128198","usu_tel": "959734603","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74279239","usu_nom": "MIGUEL ANGEL DAVILA CASTRO","usu_dni": "74279239","usu_tel": "974128025","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75923924","usu_nom": "JHAN POOL LLAUCE BANCES","usu_dni": "75923924","usu_tel": "938340657","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73982590","usu_nom": "JOSSELYN GUADALUPE BAUTISTA TICONA","usu_dni": "73982590","usu_tel": "903537872","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74574099","usu_nom": "ALEXANDER PEDRO POZO HUAYTA","usu_dni": "74574099","usu_tel": "969991383","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70908870","usu_nom": "LUIS ORLANDO PEREZ CAHUA","usu_dni": "70908870","usu_tel": "960785110","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77211129","usu_nom": "FELIX ANTONIO MENDOZA ROMERO","usu_dni": "77211129","usu_tel": "922679070","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74852746","usu_nom": "FIORELLA SOFIA HINOJOSA MEJIA","usu_dni": "74852746","usu_tel": "926904251","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70922356","usu_nom": "FLOR MARIA NIETO PALOMINO","usu_dni": "70922356","usu_tel": "948252696","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70549826","usu_nom": "JANCKER ESTEBAN LLERENA TUBILLAS","usu_dni": "70549826","usu_tel": "966610975","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72641292","usu_nom": "CAROL ROXANA ROJAS SALVADOR","usu_dni": "72641292","usu_tel": "992745897","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71541792","usu_nom": "ANTHONY JOEL ARIAS SOTOMAYOR","usu_dni": "71541792","usu_tel": "915131304","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75697549","usu_nom": "ROSA LUZ OLIDEN VILCHEZ","usu_dni": "75697549","usu_tel": "904387114","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71030492","usu_nom": "HARUMMY ESCALANTE UGARTE","usu_dni": "71030492","usu_tel": "926685022","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70272919","usu_nom": "HALBERT ARTURO TEJADA RONCEROS","usu_dni": "70272919","usu_tel": "954435276","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73526895","usu_nom": "ROBERTO SAMUEL PINO LEVANO","usu_dni": "73526895","usu_tel": "951327689","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72814253","usu_nom": "LUCERO TIPISMANA INFANTE","usu_dni": "72814253","usu_tel": "957495818","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73027692","usu_nom": "ALLISON ASUNTA CONDE VARGAS","usu_dni": "73027692","usu_tel": "931941395","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74276913","usu_nom": "FLOR DE MARIA QUICHUA ONCEBAY","usu_dni": "74276913","usu_tel": "965972153","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "48233969","usu_nom": "DIEGO ARTURO LLAPA CHACON","usu_dni": "48233969","usu_tel": "900388009","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72762073","usu_nom": "JEAN PAUL TAFUR PANDURO","usu_dni": "72762073","usu_tel": "947703427","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77101260","usu_nom": "PATRICIA MADELINE SALDAÑA CACERES","usu_dni": "77101260","usu_tel": "977869554","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "48124496","usu_nom": "MARDITH SAQUITAY NOLORBE","usu_dni": "48124496","usu_tel": "922477728","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73172396","usu_nom": "DIANA ARROYO HUACAUSE","usu_dni": "73172396","usu_tel": "944175083","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75612071","usu_nom": "VALERY ARANGO SALVATIERRA","usu_dni": "75612071","usu_tel": "935699135","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74423663","usu_nom": "BRUNO FELIX QUISPE HUANUCO","usu_dni": "74423663","usu_tel": "949004940","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70474962","usu_nom": "GUISELA RAMOS QUISPE","usu_dni": "70474962","usu_tel": "940723793","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77665592","usu_nom": "XIMENA ESQUIVEL GUEVARA","usu_dni": "77665592","usu_tel": "941020043","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76809251","usu_nom": "NILTON SEGOVIA HUILLCAHUAMAN","usu_dni": "76809251","usu_tel": "947230520","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77141513","usu_nom": "DANIEL EDUARD COICA HUAYTA","usu_dni": "77141513","usu_tel": "906007087","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74382528","usu_nom": "JEFFERSON CHRISTIAN CONDORI CCANTO","usu_dni": "74382528","usu_tel": "927871547","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74915282","usu_nom": "EMELYN YADIRA ESPINAL URBANO","usu_dni": "74915282","usu_tel": "936913567","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "47527276","usu_nom": "MELISSA GARROS BUSTOS","usu_dni": "47527276","usu_tel": "915191052","usu_zon": "LIMA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76821131","usu_nom": "EDSON BRYAN BAYGORREA CHOQUEPATA","usu_dni": "76821131","usu_tel": "941495339","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74867628","usu_nom": "JORGE SAMUEL ALFARO HANCCO","usu_dni": "74867628","usu_tel": "958520993","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75009662","usu_nom": "DANITZA ESTEFANIA PACOMPIA QUISPE","usu_dni": "75009662","usu_tel": "931479985","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73735646","usu_nom": "RUTH IDALIA TINTA TINTA","usu_dni": "73735646","usu_tel": "901946462","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77019516","usu_nom": "ROMMEL PAUL PAREDES BANDA","usu_dni": "77019516","usu_tel": "922828459","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71249999","usu_nom": "RAIZA PAOLA CUEVA HUAMAN","usu_dni": "71249999","usu_tel": "938867350","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73577129","usu_nom": "GERALDINE DEL CARMEN CAVERO BAYONA","usu_dni": "73577129","usu_tel": "902998797","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77326918","usu_nom": "FRANKER GARCIA GUERRERO","usu_dni": "77326918","usu_tel": "965678763","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72300341","usu_nom": "DENNIS PUMA LIPE","usu_dni": "72300341","usu_tel": "923956468","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76968577","usu_nom": "CESAR HUAMANI SAPACAYO","usu_dni": "76968577","usu_tel": "931603343","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "61076898","usu_nom": "BRYAN SOTOMAYOR ARAPA","usu_dni": "61076898","usu_tel": "920909153","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74079317","usu_nom": "JULIO ENRIQUE DEL AGUILA MESTANZA","usu_dni": "74079317","usu_tel": "925505721","usu_zon": "ORIENTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70557477","usu_nom": "ELVIRA GIOVANY ACOSTA ALVAREZ","usu_dni": "70557477","usu_tel": "965890030","usu_zon": "ORIENTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "46026737","usu_nom": "ANGELO MARTIN LEMOS CHOTA","usu_dni": "46026737","usu_tel": "972650233","usu_zon": "ORIENTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "46687682","usu_nom": "JIMMY HERBERT ACUÑA OSCCO","usu_dni": "46687682","usu_tel": "987097324","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71558811","usu_nom": "PIERO PINCHI ORTIZ","usu_dni": "71558811","usu_tel": "965256900","usu_zon": "ORIENTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76650173","usu_nom": "JORGE DARIO ALVAREZ RUIZ","usu_dni": "76650173","usu_tel": "972740014","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "48497378","usu_nom": "SHIRLEY STEPHANY ZAMUDIO BENITES","usu_dni": "48497378","usu_tel": "917135021","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77137958","usu_nom": "DAYANE SHEYLA HARO ROMERO","usu_dni": "77137958","usu_tel": "929763200","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76553464","usu_nom": "SANDRA CRISTINA PEÑA RIOS","usu_dni": "76553464","usu_tel": "907824616","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74876413","usu_nom": "KENLLY JEANPOOL ZAPATA JIMENEZ","usu_dni": "74876413","usu_tel": "910475076","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76819232","usu_nom": "RONALD LEDEZMA CRUZ","usu_dni": "76819232","usu_tel": "920479993","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77071292","usu_nom": "VICTOR HUGO CHARA QUISPE","usu_dni": "77071292","usu_tel": "958562187","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73356865","usu_nom": "SERGIO ROBERTO PANTA MENDOZA","usu_dni": "73356865","usu_tel": "917225492","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77033534","usu_nom": "SAYDA KARINA HUANCA JIMENEZ","usu_dni": "77033534","usu_tel": "935304969","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71965326","usu_nom": "ELIOVICHS EMANUEL ARONI CHAVEZ","usu_dni": "71965326","usu_tel": "910258200","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70895507","usu_nom": "YUSETH YENNIFER PAUCAR QUISPE","usu_dni": "70895507","usu_tel": "990465196","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74242049","usu_nom": "PRISCILA CCOA LEON","usu_dni": "74242049","usu_tel": "935831066","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73820181","usu_nom": "EBER EMANUEL VILLASANTE MAMANI","usu_dni": "73820181","usu_tel": "914420051","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74058452","usu_nom": "JULIO CÉSAR VALERIO CCUNO CHOQUEHUANCA","usu_dni": "74058452","usu_tel": "966019558","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76420056","usu_nom": "YUDITH MARLENI ISCARRA CALISAYA","usu_dni": "76420056","usu_tel": "961383896","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70130295","usu_nom": "TRINIDAD PUMA CALLATA","usu_dni": "70130295","usu_tel": "971048533","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73611497","usu_nom": "MILAGROS COILA VILCA","usu_dni": "73611497","usu_tel": "984464083","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "60456247","usu_nom": "RONY ALAN MAMANI MAMANI","usu_dni": "60456247","usu_tel": "954114186","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70650474","usu_nom": "ANTONY FABRICIO MENDOZA AROHUANCA","usu_dni": "70650474","usu_tel": "932291867","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "48732736","usu_nom": "ALEE VILLASANTE CONDORI","usu_dni": "48732736","usu_tel": "929230328","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70852843","usu_nom": "MISCHELL ROSARIO YUJRA CUSACANI","usu_dni": "70852843","usu_tel": "900498297","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73811839","usu_nom": "CESAR ANDRE COILA PANCCA","usu_dni": "73811839","usu_tel": "962137103","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77240320","usu_nom": "VICENTE JOHAN LUNA SANTOS","usu_dni": "77240320","usu_tel": "976380291","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72191886","usu_nom": "DAYELI MILAGROS MAMANI CUTIMBO","usu_dni": "72191886","usu_tel": "969088711","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70183466","usu_nom": "LUIS ENRIQUE QUISPE VARGAS","usu_dni": "70183466","usu_tel": "985477179","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75125699","usu_nom": "GONZALO FLORES HUMIPIRI","usu_dni": "75125699","usu_tel": "916216125","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "45497012","usu_nom": "YONY HUANCCO HUAMAN","usu_dni": "45497012","usu_tel": "951361248","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70772567","usu_nom": "SAÚL CALAPUJA CALAPUJA","usu_dni": "70772567","usu_tel": "978924451","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "46743723","usu_nom": "ROSA MARIA QUISPE QUISPE","usu_dni": "46743723","usu_tel": "958404042","usu_zon": "ANDINA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76590357","usu_nom": "KATIA LOPEZ BARZOLA","usu_dni": "76590357","usu_tel": "943038409","usu_zon": "AREQUIPA II","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72670147","usu_nom": "YAQUELINE MARGOT SOTO MAMANI","usu_dni": "72670147","usu_tel": "914101913","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75755953","usu_nom": "EDWIN RAMIREZ LOPEZ","usu_dni": "75755953","usu_tel": "914946654","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74620678","usu_nom": "NATALIA QUITO QUISPE","usu_dni": "74620678","usu_tel": "970289276","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "44536810","usu_nom": "MIRIAN VANESA CALLA ROMAN","usu_dni": "44536810","usu_tel": "965228331","usu_zon": "AREQUIPA I","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73479206","usu_nom": "LUIS FRANCISCO ESPIRITU YACHA","usu_dni": "73479206","usu_tel": "976007413","usu_zon": "ORIENTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74355693","usu_nom": "LETICIA ORTEGA MAMANI SULMA","usu_dni": "74355693","usu_tel": "982576996","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70993645","usu_nom": "MARICIELO ESTEFANI MUCHA ORIHUELA","usu_dni": "70993645","usu_tel": "918146719","usu_zon": "CENTRO","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73864411","usu_nom": "MARYORI LISETH CONTRERAS MEZA","usu_dni": "73864411","usu_tel": "972939880","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73322902","usu_nom": "JAZMIN QUEVEDO MANRIQUE","usu_dni": "73322902","usu_tel": "963075571","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "70555517","usu_nom": "CARLOS SHAIDD PACORI DEL CARPIO","usu_dni": "70555517","usu_tel": "946384918","usu_zon": "SUR","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71762510","usu_nom": "LUIS ALBERTO LLANOS MEDINA","usu_dni": "71762510","usu_tel": "948519541","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73418086","usu_nom": "DIANA MIRELI VASQUEZ CORONEL","usu_dni": "73418086","usu_tel": "930985415","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74488151","usu_nom": "MARCELA LLATAS TANTALEAN","usu_dni": "74488151","usu_tel": "927081535","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71555464","usu_nom": "KATERINE JAKARY LOZANO DELGADO","usu_dni": "71555464","usu_tel": "941553035","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75500001","usu_nom": "CRISTIAN OMAR MENA GONZALES","usu_dni": "75500001","usu_tel": "965255274","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77013683","usu_nom": "ZULEMA ALEJANDRIA TORRES","usu_dni": "77013683","usu_tel": "914942282","usu_zon": "NORTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71110250","usu_nom": "JHON HENRRY YLLA MANOTTUPA","usu_dni": "71110250","usu_tel": "941097343","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "76672722","usu_nom": "FIORELLA RINCON HUARANCCA","usu_dni": "76672722","usu_tel": "995883257","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73999387","usu_nom": "CALEB JOSE FASANANDO GUERRA","usu_dni": "73999387","usu_tel": "983833523","usu_zon": "ORIENTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "73064278","usu_nom": "NILTON AGUSTÍN MUGUERZA TANCHIVA","usu_dni": "73064278","usu_tel": "927389568","usu_zon": "ORIENTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "74077715","usu_nom": "ANABEL ALCÁNTARA SAJAMI","usu_dni": "74077715","usu_tel": "968303509","usu_zon": "ORIENTE","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77015729","usu_nom": "EDUARDO PANIAGUA MAMANI","usu_dni": "77015729","usu_tel": "954762088","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72694184","usu_nom": "KELLY HUAMAN HUALLPAYUNCA","usu_dni": "72694184","usu_tel": "993841193","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "77172168","usu_nom": "IRMA ESTEPHANY ZAMORA CHALLCO","usu_dni": "77172168","usu_tel": "924191977","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "45853600","usu_nom": "GLADYS MILAGROS CHAHUARA QUISPE","usu_dni": "45853600","usu_tel": "927255428","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "75973193","usu_nom": "MARCO ANTONIO PANIAGUA MAMANI","usu_dni": "75973193","usu_tel": "997162517","usu_zon": "IMPERIAL","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72372107","usu_nom": "JORGE AXEL ORTEGA MARCOS","usu_dni": "72372107","usu_tel": "900541026","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "71204162","usu_nom": "DAVID QUISPE TAYRO","usu_dni": "71204162","usu_tel": "992775290","usu_zon": "CENTRO","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72326416","usu_nom": "AYDA ROXANA HUAMAN QUINTO","usu_dni": "72326416","usu_tel": "929034636","usu_zon": "CENTRO","is_staff": False, "cat_cod": "0"},
    {"usu_cod": "72739872","usu_nom": "MILAGROS ROMERO TAQUIRE YESLIN","usu_dni": "72739872","usu_tel": "920378238","usu_zon": "LIMA II - ICA","is_staff": False, "cat_cod": "0"}
]

def run():
    print("🚀 Iniciando sembrado de datos...")
    
    with transaction.atomic():
        # 0. Sembrar Tipos de Pregunta
        for d in tipos_pregunta_data:
            tp, created = TipoPregunta.objects.update_or_create(
                tip_pre_cod=d["tip_pre_cod"],
                defaults={"tip_pre_nom": d["tip_pre_nom"]}
            )
            if created: print(f"✅ Tipo de Pregunta creado: {tp.tip_pre_nom}")

        # 1. Sembrar Categorías
        for d in categorias_data:
            cat, created = Categoria.objects.update_or_create(
                cat_cod=d["cat_cod"],
                defaults={"cat_nom": d["cat_nom"]}
            )
            if created: print(f"✅ Categoría creada: {cat.cat_nom}")

        # 1.5. Sembrar Competencias
        for d in competencias_data:
            com, created = Competencia.objects.update_or_create(
                com_cod=d["com_cod"],
                defaults={"com_nom": d["com_nom"]}
            )
            if created: print(f"✅ Competencia creada: {com.com_nom}")

        # 2. Sembrar Rangos
        for d in rangos_data:
            ran, created = Rango.objects.update_or_create(
                ran_sig=d["ran_sig"],
                defaults={
                    "ran_nom": d["ran_nom"],
                    "ran_pun_min": d["ran_pun_min"],
                    "ran_pun_max": d["ran_pun_max"]
                }
            )
            if created: print(f"✅ Rango creado: {ran.ran_nom}")

        # 3. Sembrar Usuarios
        for u in users_data:
            cat_instance = None
            if "cat_cod" in u:
                try:
                    cat_instance = Categoria.objects.get(cat_cod=u["cat_cod"])
                except Categoria.DoesNotExist:
                    print(f"⚠️ Categoría {u['cat_cod']} no encontrada para {u['usu_cod']}")

            user, created = User.objects.update_or_create(
                usu_cod=u["usu_cod"],
                defaults={
                    "username": u["usu_cod"],
                    "usu_nom": u["usu_nom"],
                    "usu_dni": u.get("usu_dni"),
                    "is_staff": u.get("is_staff", False),
                    "cat_cod": cat_instance,
                    "usu_fec_ult": timezone.now().date(),
                }
            )
            if created:
                user.set_password(u["usu_dni"])
                user.save()
                print(f"✅ Usuario creado: {user.usu_cod}")
            else:
                print(f"ℹ️ Usuario {user.usu_cod} actualizado")

    print("✨ Proceso completado con éxito.")

if __name__ == "__main__":
    run()