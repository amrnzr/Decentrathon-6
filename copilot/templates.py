"""Шаблоны черновиков на 6 языках.

Тексты составлены по реальным шаблонам админов из train (ru, uz) и правилам из rules.json.
Цитаты подставляются только из RulesIndex, поэтому выдумать пункт невозможно.
"""

GREET = {"ru": "Здравствуйте!", "kk": "Сәлеметсіз бе!", "uz": "Assalomu alaykum!", "en": "Hello!",
         "es": "¡Hola!", "pt": "Olá!"}
SIGN = {"ru": "С уважением, администрация Grand Mobile.", "kk": "Құрметпен, Grand Mobile әкімшілігі.",
        "uz": "Hurmat bilan, Grand Mobile ma'muriyati.", "en": "Regards, Grand Mobile administration.",
        "es": "Atentamente, la administración de Grand Mobile.", "pt": "Atenciosamente, administração do Grand Mobile."}

# Короткое описание нарушения для черновика
VIOLATION_DESC = {
    "insult": {"ru": "оскорбление игрока", "kk": "ойыншыны қорлау", "uz": "o'yinchini haqorat qilish",
               "en": "insulting a player", "es": "insultar a un jugador", "pt": "insultar um jogador"},
    "insult_family": {"ru": "оскорбление родных", "kk": "туыстарын қорлау", "uz": "qarindoshlarini haqorat qilish",
                      "en": "insulting a player's relatives", "es": "insultar a familiares", "pt": "insultar familiares"},
    "racism": {"ru": "разжигание розни и оскорбление по национальному или религиозному признаку",
               "kk": "ұлттық немесе діни белгі бойынша қорлау", "uz": "millat yoki din bo'yicha haqorat",
               "en": "ethnic or religious hate speech", "es": "discurso de odio étnico o religioso",
               "pt": "discurso de ódio étnico ou religioso"},
    "cheat": {"ru": "использование стороннего ПО", "kk": "бөгде бағдарламаны қолдану",
              "uz": "uchinchi tomon dasturlaridan foydalanish", "en": "use of third-party software",
              "es": "uso de software de terceros", "pt": "uso de software de terceiros"},
    "dm_gz": {"ru": "убийство или нанесение урона в Зелёной зоне", "kk": "Жасыл аймақта өлтіру немесе зақым келтіру",
              "uz": "Yashil hududda o'ldirish yoki zarar yetkazish", "en": "killing or damaging players in the Green Zone",
              "es": "matar o dañar a jugadores en la Zona Verde", "pt": "matar ou causar dano na Zona Verde"},
    "dm_house": {"ru": "убийство или урон у дома или квартиры", "kk": "үй маңында өлтіру немесе зақым келтіру",
                 "uz": "uy yonida o'ldirish yoki zarar yetkazish", "en": "killing or damaging residents at a house",
                 "es": "matar o dañar a residentes en una casa", "pt": "matar ou causar dano a moradores em uma casa"},
    "dm_rp": {"ru": "уход от RP-ситуации", "kk": "RP-жағдайдан қашу", "uz": "RP-vaziyatdan qochish",
              "en": "leaving an RP situation", "es": "abandonar una situación RP", "pt": "abandonar uma situação RP"},
    "scam": {"ru": "мошенничество с имуществом", "kk": "мүлікке қатысты алаяқтық", "uz": "mulk bo'yicha firibgarlik",
             "en": "fraud with in-game property", "es": "estafa con propiedades del juego",
             "pt": "fraude com bens do jogo"},
    "extortion": {"ru": "вымогательство", "kk": "қорқытып алу", "uz": "tovlamachilik", "en": "extortion",
                  "es": "extorsión", "pt": "extorsão"},
    "ads": {"ru": "реклама", "kk": "жарнама", "uz": "reklama", "en": "advertising", "es": "publicidad",
            "pt": "propaganda"},
    "rmt": {"ru": "сделки с имуществом за реальные деньги", "kk": "мүлікті нақты ақшаға сату",
            "uz": "mulkni haqiqiy pulga oldi-sotdi qilish", "en": "trading in-game property for real money",
            "es": "comerciar con bienes del juego por dinero real", "pt": "negociar bens do jogo por dinheiro real"},
    "nick": {"ru": "запрещённый никнейм", "kk": "тыйым салынған никнейм", "uz": "taqiqlangan nikneym",
             "en": "a forbidden nickname", "es": "un apodo prohibido", "pt": "um apelido proibido"},
    "impersonation": {"ru": "выдача себя за администрацию", "kk": "өзін әкімшілік ретінде көрсету",
                      "uz": "o'zini ma'muriyat deb tanishtirish", "en": "impersonating the administration",
                      "es": "hacerse pasar por la administración", "pt": "se passar pela administração"},
    "event": {"ru": "помеха проведению мероприятия", "kk": "іс-шараға кедергі келтіру", "uz": "tadbirga xalaqit berish",
              "en": "disrupting an event", "es": "interferir en un evento", "pt": "atrapalhar um evento"},
}

# Наказания: санкция из блока «Нарушение» соответствующего пункта rules.json,
# конкретное значение выбрано как самое частое в ответах админов train внутри диапазона правила
PUNISHMENT = {
    "mute30": {"ru": "мут на 30 минут", "kk": "30 минутқа мут", "uz": "30 daqiqaga mute", "en": "a 30-minute mute",
               "es": "silencio de 30 minutos", "pt": "mute de 30 minutos"},
    "mute60": {"ru": "мут на 60 минут", "kk": "60 минутқа мут", "uz": "60 daqiqaga mute", "en": "a 60-minute mute",
               "es": "silencio de 60 minutos", "pt": "mute de 60 minutos"},
    "mute90": {"ru": "мут на 90 минут", "kk": "90 минутқа мут", "uz": "90 daqiqaga mute", "en": "a 90-minute mute",
               "es": "silencio de 90 minutos", "pt": "mute de 90 minutos"},
    "ban7": {"ru": "блокировку персонажа на 7 дней", "kk": "кейіпкерді 7 күнге бұғаттау", "uz": "7 kunga ban",
             "en": "a 7-day character ban", "es": "bloqueo del personaje por 7 días",
             "pt": "banimento do personagem por 7 dias"},
    "ban31": {"ru": "блокировку персонажа на 31 день", "kk": "кейіпкерді 31 күнге бұғаттау", "uz": "31 kunga ban",
              "en": "a 31-day character ban", "es": "bloqueo del personaje por 31 días",
              "pt": "banimento do personagem por 31 dias"},
    "warn": {"ru": "предупреждение (WARN)", "kk": "ескерту (WARN)", "uz": "ogohlantirish (WARN)",
             "en": "a warning (WARN)", "es": "una advertencia (WARN)", "pt": "uma advertência (WARN)"},
    "demorgan60": {"ru": "деморган на 60 минут", "kk": "60 минутқа деморган", "uz": "60 daqiqaga demorgan",
                   "en": "60 minutes in demorgan", "es": "60 minutos de demorgan", "pt": "60 minutos de demorgan"},
    "demorgan120": {"ru": "деморган на 120 минут", "kk": "120 минутқа деморган", "uz": "120 daqiqaga demorgan",
                    "en": "120 minutes in demorgan", "es": "120 minutos de demorgan", "pt": "120 minutos de demorgan"},
    "verbal": {"ru": "устное предупреждение", "kk": "ауызша ескерту", "uz": "og'zaki ogohlantirish",
               "en": "a verbal warning", "es": "una advertencia verbal", "pt": "uma advertência verbal"},
}

T = {
    # ---------------------------------------------------------------- жалобы
    "approve": {
        "ru": "Ваша жалоба рассмотрена. В действиях игрока {nick} подтверждается нарушение {rule}: {desc}. "
              "Игрок {nick} получит {punishment}.",
        "kk": "Шағымыңыз қаралды. {nick} ойыншысының әрекетінде {rule} бұзылғаны расталды: {desc}. "
              "{nick} ойыншысына жаза: {punishment}.",
        "uz": "Shikoyatingiz ko'rib chiqildi. {nick} o'yinchisining harakatlarida {rule} buzilgani tasdiqlandi: {desc}. "
              "{nick} o'yinchisiga jazo: {punishment}.",
        "en": "Your complaint has been reviewed. Player {nick} violated {rule}: {desc}. "
              "Player {nick} will receive {punishment}.",
        "es": "Su queja ha sido revisada. El jugador {nick} infringió el {rule}: {desc}. "
              "El jugador {nick} recibirá {punishment}.",
        "pt": "Sua denúncia foi analisada. O jogador {nick} violou o {rule}: {desc}. "
              "O jogador {nick} receberá {punishment}.",
    },
    "need_video": {
        "ru": "Благодарим за жалобу. Для проверки такого нарушения нужна видеофиксация: по скриншотам нельзя "
              "однозначно установить, что произошло ({r1}). Загрузите запись на разрешённую площадку "
              "(YouTube, Rutube, imgur, Яндекс Диск, Google Диск, {r2}) и подайте новую жалобу.",
        "kk": "Шағымыңызға рақмет. Мұндай бұзушылықты тексеру үшін бейнежазба қажет: скриншоттар бойынша "
              "не болғанын нақты анықтау мүмкін емес ({r1}). Жазбаны рұқсат етілген платформаға "
              "(YouTube, Rutube, imgur, Яндекс Диск, Google Диск, {r2}) жүктеп, жаңа шағым беріңіз.",
        "uz": "Shikoyatingiz uchun rahmat. Bunday qoidabuzarlikni tekshirish uchun video dalil (videofiksatsiya) kerak: "
              "skrinshotlar orqali nima bo'lganini aniq bilib bo'lmaydi ({r1}). Videoni ruxsat etilgan platformaga "
              "(YouTube, Rutube, imgur, Yandex Disk, Google Disk, {r2}) yuklang va yangi shikoyat yuboring.",
        "en": "Thank you for your complaint. This type of violation can only be verified with a video recording: "
              "screenshots do not show clearly what happened ({r1}). Upload the video to an allowed platform "
              "(YouTube, Rutube, imgur, Yandex Disk, Google Drive, {r2}) and submit a new complaint.",
        "es": "Gracias por su queja. Este tipo de infracción solo se puede comprobar con un video: las capturas "
              "no muestran con claridad lo que pasó ({r1}). Suba el video a una plataforma permitida "
              "(YouTube, Rutube, imgur, Yandex Disk, Google Drive, {r2}) y envíe una nueva queja.",
        "pt": "Obrigado pela denúncia. Esse tipo de infração só pode ser verificado com vídeo: as capturas de tela "
              "não mostram com clareza o que aconteceu ({r1}). Envie o vídeo para uma plataforma permitida "
              "(YouTube, Rutube, imgur, Yandex Disk, Google Drive, {r2}) e faça uma nova denúncia.",
    },
    "invalid_empty": {
        "ru": "Жалоба не может быть рассмотрена: в описании нет сути произошедшего ({r1}). Подайте новую жалобу: "
              "укажите никнейм нарушителя, что именно произошло, и приложите доказательства ({r2}).",
        "kk": "Шағым қаралмайды: сипаттамада оқиғаның мән-жайы көрсетілмеген ({r1}). Жаңа шағым беріңіз: "
              "бұзушының никнеймін, не болғанын нақты жазып, дәлелдерді тіркеңіз ({r2}).",
        "uz": "Shikoyat ko'rib chiqilmaydi: tavsifda nima bo'lgani aniq yozilmagan ({r1}). Yangi shikoyat yuboring: "
              "qoidabuzarning nikneymini, aynan nima bo'lganini yozing va dalillarni ilova qiling ({r2}).",
        "en": "The complaint cannot be reviewed: the description does not explain what happened ({r1}). "
              "Please submit a new complaint with the offender's nickname, what exactly happened and evidence ({r2}).",
        "es": "La queja no puede ser revisada: la descripción no explica lo que pasó ({r1}). Envíe una nueva queja "
              "con el apodo del infractor, lo que ocurrió exactamente y las pruebas ({r2}).",
        "pt": "A denúncia não pode ser analisada: a descrição não explica o que aconteceu ({r1}). Faça uma nova "
              "denúncia com o apelido do infrator, o que aconteceu exatamente e as provas ({r2}).",
    },
    "invalid_not_complaint": {
        "ru": "Раздел жалоб предназначен только для сообщений о нарушениях правил, вопросы и технические проблемы "
              "здесь не рассматриваются ({r1}). С вопросом обратитесь через репорт в игре или в Discord проекта.",
        "kk": "Шағымдар бөлімі тек ереже бұзушылықтар туралы хабарлауға арналған, сұрақтар мен техникалық "
              "мәселелер мұнда қаралмайды ({r1}). Сұрағыңызды ойындағы репорт арқылы немесе жобаның Discord-ына жазыңыз.",
        "uz": "Shikoyatlar bo'limi faqat qoidabuzarliklar haqida xabar berish uchun, savollar va texnik muammolar "
              "bu yerda ko'rib chiqilmaydi ({r1}). Savolingizni o'yindagi report orqali yoki loyiha Discord'iga yozing.",
        "en": "The complaints section is only for reporting rule violations; questions and technical issues are not "
              "handled here ({r1}). Please ask via the in-game report or the project's Discord.",
        "es": "La sección de quejas es solo para reportar infracciones; aquí no se atienden preguntas ni problemas "
              "técnicos ({r1}). Pregunte por el reporte del juego o en el Discord del proyecto.",
        "pt": "A seção de denúncias é apenas para infrações das regras; dúvidas e problemas técnicos não são "
              "tratados aqui ({r1}). Pergunte pelo report do jogo ou no Discord do projeto.",
    },
    "invalid_toxic": {
        "ru": "Жалоба не может быть рассмотрена: её текст содержит оскорбления или ненормативную лексику ({r1}). "
              "Подайте новую жалобу с корректным описанием ситуации и доказательствами.",
        "kk": "Шағым қаралмайды: мәтінінде қорлау немесе былапыт сөздер бар ({r1}). Жағдайды әдепті түрде "
              "сипаттап, дәлелдерімен жаңа шағым беріңіз.",
        "uz": "Shikoyat ko'rib chiqilmaydi: matnida haqorat yoki so'kinish bor ({r1}). Vaziyatni odob bilan "
              "tasvirlab, dalillar bilan yangi shikoyat yuboring.",
        "en": "The complaint cannot be reviewed: its text contains insults or profanity ({r1}). Please submit a new "
              "complaint with a polite description and evidence.",
        "es": "La queja no puede ser revisada: su texto contiene insultos o groserías ({r1}). Envíe una nueva queja "
              "con una descripción correcta y pruebas.",
        "pt": "A denúncia não pode ser analisada: o texto contém insultos ou palavrões ({r1}). Faça uma nova "
              "denúncia com uma descrição adequada e provas.",
    },
    "duplicate": {
        "ru": "Эта жалоба дублирует уже поданную, поэтому повторно не рассматривается ({r1}). "
              "Ожидайте ответа по первой жалобе.",
        "kk": "Бұл шағым бұрын берілген шағымды қайталайды, сондықтан қайта қаралмайды ({r1}). "
              "Бірінші шағымыңыз бойынша жауапты күтіңіз.",
        "uz": "Ushbu shikoyat avval yuborilgan shikoyatning takrori, shu sababli qayta ko'rib chiqilmaydi ({r1}). "
              "Birinchi shikoyatingiz bo'yicha javobni kuting.",
        "en": "This complaint duplicates one you already submitted, so it will not be reviewed again ({r1}). "
              "Please wait for the answer to the first complaint.",
        "es": "Esta queja duplica una que ya envió, por lo que no se revisará de nuevo ({r1}). "
              "Espere la respuesta a la primera queja.",
        "pt": "Esta denúncia duplica uma já enviada, por isso não será analisada novamente ({r1}). "
              "Aguarde a resposta da primeira denúncia.",
    },
    "appeal": {
        "ru": "Ваша жалоба на выданное наказание получена и передана старшей администрации. Администратор, "
              "выдавший наказание, предоставит доказательства, после проверки вы получите ответ. {extra}",
        "kk": "Берілген жазаға қатысты шағымыңыз қабылданып, аға әкімшілікке жіберілді. Жазаны берген әкімші "
              "дәлелдерін ұсынады, тексерістен кейін жауап аласыз. {extra}",
        "uz": "Berilgan jazo bo'yicha shikoyatingiz qabul qilindi va katta ma'muriyatga yuborildi. Jazoni bergan "
              "administrator dalillarni taqdim etadi, tekshiruvdan so'ng javob olasiz. {extra}",
        "en": "Your appeal against the punishment has been received and passed to senior administration. The admin "
              "who issued it will provide evidence, and you will get an answer after the review. {extra}",
        "es": "Su apelación contra la sanción fue recibida y enviada a la administración superior. El administrador "
              "que la aplicó presentará pruebas y recibirá una respuesta tras la revisión. {extra}",
        "pt": "Sua apelação contra a punição foi recebida e enviada à administração superior. O administrador que a "
              "aplicou apresentará provas, e você receberá uma resposta após a análise. {extra}",
    },
    "appeal_extra": {
        "ru": "Если вы ещё не приложили скриншот наказания и не написали, с чем именно не согласны, дополните "
              "жалобу: общие формулировки без фактов отклоняются ({r1}, {r2}).",
        "kk": "Егер жаза скриншотын тіркемесеңіз және нақты неге келіспейтініңізді жазбасаңыз, шағымды толықтырыңыз: "
              "нақты фактілерсіз жалпылама тұжырымдар қабылданбайды ({r1}, {r2}).",
        "uz": "Agar jazo skrinshotini ilova qilmagan va aynan nimaga rozi emasligingizni yozmagan bo'lsangiz, "
              "shikoyatni to'ldiring: faktlarsiz umumiy so'zlar rad etiladi ({r1}, {r2}).",
        "en": "If you have not attached a screenshot of the punishment or explained what exactly you disagree with, "
              "please add it: general statements without facts are rejected ({r1}, {r2}).",
        "es": "Si no adjuntó una captura de la sanción ni explicó con qué no está de acuerdo, complete la queja: "
              "las frases generales sin hechos se rechazan ({r1}, {r2}).",
        "pt": "Se você não anexou a captura da punição nem explicou com o que discorda, complemente a denúncia: "
              "frases genéricas sem fatos são rejeitadas ({r1}, {r2}).",
    },
    "admin_misconduct": {
        "ru": "Ваша жалоба на действия администратора передана куратору сервера для проверки. Жалобы на "
              "администрацию подаются через этот раздел в течение 2 дней ({r1}). Решение примет руководство "
              "после изучения доказательств.",
        "kk": "Әкімшінің әрекетіне қатысты шағымыңыз тексеру үшін сервер кураторына жіберілді. Әкімшілікке "
              "шағым осы бөлім арқылы 2 күн ішінде беріледі ({r1}). Шешімді басшылық дәлелдерді қарағаннан кейін қабылдайды.",
        "uz": "Administrator harakatlari ustidan shikoyatingiz tekshirish uchun server kuratoriga yuborildi. "
              "Ma'muriyat ustidan shikoyatlar shu bo'lim orqali 2 kun ichida beriladi ({r1}). Qarorni rahbariyat "
              "dalillarni o'rganib chiqqandan so'ng qabul qiladi.",
        "en": "Your complaint about the administrator has been passed to the server curator for review. Complaints "
              "about admins are submitted in this section within 2 days ({r1}). Management will decide after "
              "reviewing the evidence.",
        "es": "Su queja sobre el administrador fue enviada al curador del servidor para revisión. Las quejas sobre "
              "administradores se envían en esta sección dentro de 2 días ({r1}). La dirección decidirá tras "
              "revisar las pruebas.",
        "pt": "Sua denúncia sobre o administrador foi enviada ao curador do servidor para análise. Denúncias sobre "
              "administradores são feitas nesta seção em até 2 dias ({r1}). A direção decidirá após analisar as provas.",
    },
    "complaint_review": {
        "ru": "Ваша жалоба принята и будет рассмотрена администратором. Жалоба рассматривается при наличии "
              "объективных доказательств нарушения ({r1}).",
        "kk": "Шағымыңыз қабылданды, оны әкімші қарайды. Шағым бұзушылықтың объективті дәлелдері болған "
              "жағдайда қаралады ({r1}).",
        "uz": "Shikoyatingiz qabul qilindi va administrator tomonidan ko'rib chiqiladi. Shikoyat qoidabuzarlikning "
              "obyektiv dalillari bo'lgandagina ko'rib chiqiladi ({r1}).",
        "en": "Your complaint has been accepted and will be reviewed by an administrator. Complaints are reviewed "
              "only with objective evidence of the violation ({r1}).",
        "es": "Su queja fue aceptada y será revisada por un administrador. Las quejas se revisan solo con pruebas "
              "objetivas de la infracción ({r1}).",
        "pt": "Sua denúncia foi aceita e será analisada por um administrador. As denúncias são analisadas apenas "
              "com provas objetivas da infração ({r1}).",
    },
    # ---------------------------------------------------------------- репорты
    "clarify": {
        "ru": "уточните ваш вопрос или жалобу.",
        "kk": "сұрағыңызды немесе шағымыңызды нақтылаңыз.",
        "uz": "savolingiz yoki shikoyatingizga aniqlik kiriting.",
        "en": "please clarify your question or complaint.",
        "es": "por favor, aclare su pregunta o queja.",
        "pt": "por favor, explique sua dúvida ou denúncia.",
    },
    "spam": {
        "ru": "уточните ваш вопрос или жалобу. Оффтоп и флуд в репорт запрещены ({r1}).",
        "kk": "сұрағыңызды немесе шағымыңызды нақтылаңыз. Репортқа оффтоп пен флуд жазуға болмайды ({r1}).",
        "uz": "savolingiz yoki shikoyatingizni aniqlashtiring. Reportga offtop va flud yozish taqiqlangan ({r1}).",
        "en": "please clarify your question or complaint. Off-topic messages and flood in the report are not allowed ({r1}).",
        "es": "aclare su pregunta o queja. El offtopic y el flood en el reporte están prohibidos ({r1}).",
        "pt": "explique sua dúvida ou denúncia. Offtopic e flood no report são proibidos ({r1}).",
    },
    "help_vehicle": {
        "ru": "нажмите кнопку эвакуатора на спидометре.",
        "kk": "спидометрдегі эвакуатор батырмасын басыңыз.",
        "uz": "spidometrdagi evakuator tugmasini bosing.",
        "en": "press the tow truck button on the speedometer.",
        "es": "pulse el botón de grúa en el velocímetro.",
        "pt": "aperte o botão de guincho no velocímetro.",
    },
    "help_admin": {
        "ru": "слежу за вами.",
        "kk": "сізді бақылаудамын.",
        "uz": "sizni kuzatyapman.",
        "en": "I'm watching, help is on the way.",
        "es": "le estoy observando, enseguida le ayudo.",
        "pt": "estou acompanhando você, já vou ajudar.",
    },
    "no_teleport": {
        "ru": "не телепортируем, данная услуга не предоставляется ({r1}).",
        "kk": "телепорт жасамаймыз, бұл қызмет көрсетілмейді ({r1}).",
        "uz": "teleport qilmaymiz, bu xizmat ko'rsatilmaydi ({r1}).",
        "en": "we don't teleport players, this service is not provided ({r1}).",
        "es": "no teletransportamos jugadores, este servicio no se ofrece ({r1}).",
        "pt": "não teleportamos jogadores, esse serviço não é oferecido ({r1}).",
    },
    "jail": {
        "ru": "не снимаем наказания. Если считаете его несправедливым, напишите жалобу с доказательствами.",
        "kk": "жазаны алып тастамаймыз. Әділетсіз деп санасаңыз, дәлелдеріңізбен шағым жазыңыз.",
        "uz": "jazolarni olib tashlamaymiz. Adolatsiz deb hisoblasangiz, dalillar bilan shikoyat yozing.",
        "en": "we don't remove punishments. If you think it was unfair, file a complaint with evidence.",
        "es": "no retiramos sanciones. Si cree que fue injusta, envíe una queja con pruebas.",
        "pt": "não retiramos punições. Se achar injusta, faça uma denúncia com provas.",
    },
    "report_complaint": {
        "ru": "слежу за игроком. При наличии доказательств напишите жалобу.",
        "kk": "ойыншыны бақылаудамын. Дәлелдеріңіз болса, шағым жазыңыз.",
        "uz": "o'yinchini kuzatyapman. Sizda dalillar bo'lsa, shikoyat yozing.",
        "en": "I'm watching the player. If you have evidence, file a complaint.",
        "es": "estoy vigilando al jugador. Si tiene pruebas, envíe una queja.",
        "pt": "estou acompanhando o jogador. Se tiver provas, faça uma denúncia.",
    },
    "question_forward": {
        "ru": "ваш вопрос передал, ожидайте.",
        "kk": "сұрағыңызды жеткіздім, күтіңіз.",
        "uz": "savolingizni yetkazdim, kuting.",
        "en": "I've passed your question on, please wait.",
        "es": "transmití su pregunta, espere por favor.",
        "pt": "encaminhei sua pergunta, aguarde por favor.",
    },
    "rules_answer": {
        "ru": "это регулирует {rule}: {body}",
        "kk": "бұл мәселені {rule} реттейді. Толық мәтінін ойын ережелерінен қараңыз.",
        "uz": "bu masala {rule} bilan tartibga solinadi. To'liq matnini o'yin qoidalaridan ko'ring.",
        "en": "this is covered by {rule}. Please see the full text in the game rules.",
        "es": "esto está regulado por el {rule}. Consulte el texto completo en las reglas del juego.",
        "pt": "isso é regulado pelo {rule}. Veja o texto completo nas regras do jogo.",
    },
    "account": {
        "ru": "Обращение по аккаунту передано специалисту поддержки. Никому не сообщайте пароль и коды "
              "подтверждения. {extra}",
        "kk": "Аккаунтқа қатысты өтінішіңіз қолдау маманына жіберілді. Құпиясөз бен растау кодтарын ешкімге "
              "айтпаңыз. {extra}",
        "uz": "Akkaunt bo'yicha murojaatingiz qo'llab-quvvatlash mutaxassisiga yuborildi. Parol va tasdiqlash "
              "kodlarini hech kimga aytmang. {extra}",
        "en": "Your account request has been passed to a support specialist. Never share your password or "
              "verification codes. {extra}",
        "es": "Su solicitud sobre la cuenta fue enviada a un especialista de soporte. No comparta su contraseña ni "
              "códigos de verificación. {extra}",
        "pt": "Sua solicitação sobre a conta foi enviada a um especialista do suporte. Não compartilhe sua senha "
              "nem códigos de verificação. {extra}",
    },
    "account_extra": {
        "ru": "Обратите внимание: игрок сам отвечает за сохранность аккаунта и имущества, и администрация не "
              "восстанавливает потерянное или переданное имущество ({r1}).",
        "kk": "Назар аударыңыз: аккаунт пен мүліктің сақталуына ойыншының өзі жауап береді, әкімшілік жоғалған "
              "немесе берілген мүлікті қалпына келтірмейді ({r1}).",
        "uz": "E'tibor bering: akkaunt va mulk xavfsizligi uchun o'yinchining o'zi javobgar, ma'muriyat yo'qolgan "
              "yoki berilgan mulkni tiklamaydi ({r1}).",
        "en": "Please note: players are responsible for their account and property, and the administration does "
              "not restore lost or transferred property ({r1}).",
        "es": "Tenga en cuenta: cada jugador es responsable de su cuenta y bienes, y la administración no restaura "
              "bienes perdidos o transferidos ({r1}).",
        "pt": "Observação: o jogador é responsável pela conta e pelos bens, e a administração não restaura bens "
              "perdidos ou transferidos ({r1}).",
    },
    "payment": {
        "ru": "Вопрос по платежу передан в техническую поддержку. Чтобы ускорить проверку, укажите дату, сумму и "
              "способ оплаты (данные карты не присылайте).",
        "kk": "Төлем бойынша сұрағыңыз техникалық қолдауға жіберілді. Тексеруді жеделдету үшін төлем күнін, "
              "сомасын және тәсілін жазыңыз (карта деректерін жібермеңіз).",
        "uz": "To'lov bo'yicha savolingiz texnik yordamga yuborildi. Tekshiruvni tezlashtirish uchun to'lov sanasi, "
              "summasi va usulini yozing (karta ma'lumotlarini yubormang).",
        "en": "Your payment question has been passed to technical support. To speed up the check, send the date, "
              "amount and payment method (do not send card details).",
        "es": "Su consulta de pago fue enviada al soporte técnico. Para agilizar la revisión, indique la fecha, el "
              "monto y el método de pago (no envíe datos de la tarjeta).",
        "pt": "Sua dúvida sobre pagamento foi enviada ao suporte técnico. Para agilizar, informe a data, o valor e "
              "a forma de pagamento (não envie dados do cartão).",
    },
}


USED: list[str] = []  # отладка: какие шаблоны использовал последний вызов triage


def get(key: str, lang: str) -> str:
    USED.append(key)
    variants = T[key]
    return variants.get(lang) or variants.get("en") or variants["ru"]


# В репортах админы отвечают коротко: «Приветствую, слежу за вами.»
REPORT_GREET = {"ru": "Приветствую,", "kk": "Сәлеметсіз бе,", "uz": "Assalomu alaykum,", "en": "Hello,",
                "es": "Hola,", "pt": "Olá,"}


def wrap(body: str, lang: str, kind: str) -> str:
    """Приветствие + тело. Подпись только для жалоб, как в ответах админов из лаунчера."""
    body = body.strip()
    if kind == "report":
        g = REPORT_GREET.get(lang, REPORT_GREET["en"])
        if body and not body[:2].isupper():  # не трогаем аббревиатуры в начале
            body = body[0].lower() + body[1:]
    else:
        g = GREET.get(lang, GREET["en"])
        if body:
            body = body[0].upper() + body[1:]
    text = f"{g} {body}".strip()
    if kind == "complaint":
        text += "\n\n" + SIGN.get(lang, SIGN["en"])
    import re
    return re.sub(r"[ \t]{2,}", " ", text).replace(" .", ".").replace(" :", ":").strip()
