from sqlalchemy import select

from app.core.enums import NivelDificultad, TipoComida
from app.db.session import SessionLocal
from app.models.ingrediente import Ingrediente
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.receta_tipo_comida import RecetaTipoComida


# Formato de "pasos": cada paso termina con un punto (.) y los pasos se separan
# con un espacio. No usar puntos dentro de un paso (decimales, abreviaturas, etc.)
# para no cortar un paso por error al separarlos.
RECETAS_INICIALES = [
    {
        "nombre": "Avena con banana",
        "pasos": "Calentar la leche en una olla a fuego medio. Agregar la avena y revolver 3 a 5 minutos hasta que espese. Pelar la banana y cortarla en rodajas. Servir la avena en un bowl y colocar la banana por encima.",
        "tiempo_preparacion": 10,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Avena", 50, "g"),
            ("Banana", 1, "unidad"),
            ("Leche", 200, "ml"),
        ],
    },
    {
        "nombre": "Arroz con pollo",
        "pasos": "Hervir el arroz en abundante agua con una pizca de sal unos 15 minutos y escurrirlo. Cortar el pollo en trozos chicos. Calentar el aceite de oliva en una sartén a fuego medio. Cocinar el pollo 8 a 10 minutos, dándolo vuelta, hasta que no quede rosado por dentro. Mezclar el pollo con el arroz y servir caliente.",
        "tiempo_preparacion": 35,
        "dificultad": NivelDificultad.INTERMEDIO,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Arroz", 150, "g"),
            ("Pollo", 200, "g"),
            ("Aceite de oliva", 15, "ml"),
        ],
    },
    {
        "nombre": "Ensalada de garbanzos",
        "pasos": "Si los garbanzos son secos, remojarlos desde la noche anterior y hervirlos hasta que estén tiernos. Si son de lata, escurrirlos y enjuagarlos. Lavar el tomate y la zanahoria. Cortar el tomate en cubos y rallar la zanahoria. Mezclar todo en un bowl y servir.",
        "tiempo_preparacion": 20,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Garbanzos", 150, "g"),
            ("Tomate", 1, "unidad"),
            ("Zanahoria", 1, "unidad"),
        ],
    },
    {
        "nombre": "Omelette de espinaca",
        "pasos": "Lavar la espinaca y picarla. Batir los huevos en un bowl con una pizca de sal. Calentar una sartén antiadherente a fuego medio. Verter los huevos y dejar cuajar 1 minuto. Agregar la espinaca y el queso sobre una mitad. Doblar el omelette y cocinar 2 minutos más hasta que el queso se derrita.",
        "tiempo_preparacion": 15,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.ALMUERZO],
        "ingredientes": [
            ("Huevo", 2, "unidad"),
            ("Espinaca", 50, "g"),
            ("Queso", 30, "g"),
        ],
    },
    {
        "nombre": "Merluza con arroz",
        "pasos": "Hervir el arroz en abundante agua con una pizca de sal unos 15 minutos y escurrirlo. Secar la merluza con papel de cocina y salarla. Calentar el aceite de oliva en una sartén a fuego medio. Cocinar la merluza 3 a 4 minutos de cada lado hasta que se desarme fácilmente con el tenedor. Servir la merluza junto con el arroz.",
        "tiempo_preparacion": 30,
        "dificultad": NivelDificultad.INTERMEDIO,
        "porciones_base": 1,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Merluza", 200, "g"),
            ("Arroz", 150, "g"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },


    {
        "nombre": "Avena con manzana",
        "pasos": "Lavar la manzana y cortarla en cubos chicos. Calentar la leche en una olla a fuego medio. Agregar la avena y revolver 3 a 5 minutos hasta que espese. Incorporar la manzana y mezclar. Servir caliente.",
        "tiempo_preparacion": 10,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Avena", 50, "g"),
            ("Leche", 200, "ml"),
            ("Manzana", 1, "unidad"),
        ],
    },
    {
        "nombre": "Banana con almendras",
        "pasos": "Pelar la banana y cortarla en rodajas. Picar las almendras en trozos chicos. Servir la banana en un plato y espolvorear las almendras por encima.",
        "tiempo_preparacion": 5,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Banana", 1, "unidad"),
            ("Almendra", 25, "g"),
        ],
    },
    {
        "nombre": "Huevos revueltos con tomate",
        "pasos": "Lavar el tomate y cortarlo en cubos chicos. Batir los huevos con una pizca de sal. Calentar el aceite de oliva en una sartén a fuego medio. Cocinar el tomate 2 minutos. Agregar los huevos y revolver con una cuchara de madera hasta que cuajen por completo.",
        "tiempo_preparacion": 10,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.ALMUERZO],
        "ingredientes": [
            ("Huevo", 2, "unidad"),
            ("Tomate", 1, "unidad"),
            ("Aceite de oliva", 5, "ml"),
        ],
    },
    {
        "nombre": "Manzana con mantequilla de maní casera",
        "pasos": "Procesar el maní en un procesador o licuadora potente hasta obtener una pasta. Raspar los bordes y seguir procesando si hace falta. Lavar la manzana, quitarle el centro y cortarla en gajos. Servir los gajos con la mantequilla de maní.",
        "tiempo_preparacion": 15,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Manzana", 1, "unidad"),
            ("Maní", 40, "g"),
        ],
    },
    {
        "nombre": "Omelette de queso",
        "pasos": "Cortar el queso en cubos chicos o rallarlo. Batir los huevos con una pizca de sal. Calentar una sartén antiadherente a fuego medio. Verter los huevos y dejar cuajar 1 minuto. Agregar el queso sobre una mitad y doblar el omelette. Cocinar 2 minutos más de cada lado.",
        "tiempo_preparacion": 12,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Huevo", 2, "unidad"),
            ("Queso", 40, "g"),
        ],
    },
    {
        "nombre": "Ensalada de lentejas",
        "pasos": "Enjuagar las lentejas. Hervirlas en agua 20 a 25 minutos hasta que estén tiernas y escurrirlas. Dejarlas enfriar. Cortar el tomate en cubos y rallar la zanahoria. Mezclar todo en un bowl y servir.",
        "tiempo_preparacion": 30,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Lentejas", 150, "g"),
            ("Tomate", 1, "unidad"),
            ("Zanahoria", 1, "unidad"),
        ],
    },
    {
        "nombre": "Pollo con espinaca",
        "pasos": "Cortar el pollo en trozos y salarlo. Calentar la mitad del aceite de oliva en una sartén a fuego medio. Cocinar el pollo 8 a 10 minutos, dándolo vuelta, hasta que no quede rosado por dentro. Reservar el pollo. En la misma sartén calentar el resto del aceite y saltear la espinaca lavada 2 a 3 minutos. Servir el pollo junto con la espinaca.",
        "tiempo_preparacion": 30,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Pollo", 200, "g"),
            ("Espinaca", 100, "g"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Arroz con lentejas",
        "pasos": "Enjuagar las lentejas y hervirlas en agua 20 a 25 minutos hasta que estén tiernas. Hervir el arroz aparte en agua con una pizca de sal unos 15 minutos. Escurrir ambos ingredientes. Mezclarlos en un bowl y servir caliente.",
        "tiempo_preparacion": 35,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Arroz", 120, "g"),
            ("Lentejas", 100, "g"),
        ],
    },
    {
        "nombre": "Ensalada de atun y garbanzos",
        "pasos": "Escurrir los garbanzos cocidos y enjuagarlos. Escurrir el atún. Lavar el tomate y cortarlo en cubos. Mezclar los garbanzos, el atún y el tomate en un bowl. Servir.",
        "tiempo_preparacion": 15,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Atún", 120, "g"),
            ("Garbanzos", 120, "g"),
            ("Tomate", 1, "unidad"),
        ],
    },
    {
        "nombre": "Carne con zanahorias",
        "pasos": "Pelar las zanahorias, cortarlas en rodajas y hervirlas 10 a 12 minutos hasta que estén tiernas. Salar la carne. Calentar el aceite de oliva en una plancha o sartén a fuego medio-alto. Cocinar la carne 4 a 5 minutos de cada lado hasta que esté bien cocida. Dejar reposar la carne 2 minutos. Servir con las zanahorias.",
        "tiempo_preparacion": 30,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Carne vacuna", 200, "g"),
            ("Zanahoria", 2, "unidad"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Merluza con espinaca",
        "pasos": "Precalentar el horno a 200 grados. Colocar la merluza en una fuente, salarla y rociarla con la mitad del aceite de oliva. Hornear 15 a 20 minutos hasta que se desarme fácilmente con el tenedor. Mientras tanto, calentar el resto del aceite en una sartén y saltear la espinaca lavada 2 a 3 minutos. Servir la merluza con la espinaca.",
        "tiempo_preparacion": 30,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Merluza", 200, "g"),
            ("Espinaca", 100, "g"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Tortilla de espinaca",
        "pasos": "Lavar la espinaca y picarla. Batir los huevos con una pizca de sal y mezclarlos con la espinaca. Calentar una sartén antiadherente a fuego medio. Verter la mezcla y cocinar 4 a 5 minutos hasta que los bordes cuajen. Dar vuelta la tortilla con ayuda de un plato. Cocinar 3 minutos más del otro lado.",
        "tiempo_preparacion": 20,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Huevo", 2, "unidad"),
            ("Espinaca", 100, "g"),
        ],
    },
    {
        "nombre": "Ensalada de arroz y atun",
        "pasos": "Hervir el arroz en agua con una pizca de sal unos 15 minutos y escurrirlo. Dejarlo enfriar por completo. Escurrir el atún y cortar el tomate en cubos. Mezclar el arroz con el atún y el tomate. Servir frío.",
        "tiempo_preparacion": 25,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Arroz", 120, "g"),
            ("Atún", 100, "g"),
            ("Tomate", 1, "unidad"),
        ],
    },
    {
        "nombre": "Manzana con queso y almendras",
        "pasos": "Lavar la manzana, quitarle el centro y cortarla en gajos. Cortar el queso en cubos o láminas. Servir todo en un plato y acompañar con las almendras.",
        "tiempo_preparacion": 5,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.MERIENDA],
        "ingredientes": [
            ("Manzana", 1, "unidad"),
            ("Queso", 40, "g"),
            ("Almendra", 20, "g"),
        ],
    },
    {
        "nombre": "Licuado de banana y avena",
        "pasos": "Pelar la banana y cortarla en trozos. Colocar en la licuadora la banana, la leche y la avena. Licuar 30 segundos hasta que la mezcla quede homogénea. Servir de inmediato.",
        "tiempo_preparacion": 5,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Banana", 1, "unidad"),
            ("Leche", 200, "ml"),
            ("Avena", 30, "g"),
        ],
    },
    {
        "nombre": "Avena con almendras y banana",
        "pasos": "Calentar la leche en una olla a fuego medio. Agregar la avena y revolver 3 a 5 minutos hasta que espese. Pelar la banana y cortarla en rodajas. Picar las almendras. Servir la avena y decorar con la banana y las almendras.",
        "tiempo_preparacion": 12,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Avena", 50, "g"),
            ("Leche", 200, "ml"),
            ("Banana", 1, "unidad"),
            ("Almendra", 20, "g"),
        ],
    },
    {
        "nombre": "Licuado de manzana y avena",
        "pasos": "Lavar la manzana, quitarle el centro y cortarla en trozos. Colocar en la licuadora la manzana, la leche y la avena. Licuar 30 segundos hasta que la mezcla quede homogénea. Servir de inmediato.",
        "tiempo_preparacion": 7,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Manzana", 1, "unidad"),
            ("Avena", 40, "g"),
            ("Leche", 200, "ml"),
        ],
    },
    {
        "nombre": "Ensalada de frutas con mani",
        "pasos": "Pelar la banana y cortarla en rodajas. Lavar la manzana, quitarle el centro y cortarla en cubos. Picar el maní. Mezclar las frutas en un bowl y espolvorear el maní por encima.",
        "tiempo_preparacion": 10,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Banana", 1, "unidad"),
            ("Manzana", 1, "unidad"),
            ("Maní", 20, "g"),
        ],
    },
    {
        "nombre": "Bolitas de avena y mani",
        "pasos": "Procesar el maní hasta obtener una pasta. Pisar la banana con un tenedor hasta formar un puré. Mezclar la pasta de maní, la banana y la avena en un bowl. Formar bolitas del tamaño de una nuez con las manos. Refrigerar 15 minutos antes de servir.",
        "tiempo_preparacion": 20,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.MERIENDA],
        "ingredientes": [
            ("Avena", 60, "g"),
            ("Maní", 40, "g"),
            ("Banana", 1, "unidad"),
        ],
    },
    {
        "nombre": "Arroz con carne y tomate",
        "pasos": "Hervir el arroz en agua con una pizca de sal unos 15 minutos y escurrirlo. Cortar la carne en tiras finas y salarla. Calentar el aceite de oliva en una sartén a fuego medio-alto. Cocinar la carne 6 a 8 minutos hasta que no quede rosada. Agregar el tomate picado y cocinar 3 minutos más. Servir la carne con el arroz.",
        "tiempo_preparacion": 35,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Arroz", 120, "g"),
            ("Carne vacuna", 180, "g"),
            ("Tomate", 1, "unidad"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Guiso de garbanzos y espinaca",
        "pasos": "Remojar los garbanzos desde la noche anterior. Hervirlos en una olla con agua 40 a 45 minutos hasta que estén tiernos. Cortar el tomate y la zanahoria en cubos. Agregar el tomate y la zanahoria a la olla y cocinar 10 minutos. Incorporar la espinaca lavada y cocinar 3 minutos más. Servir caliente.",
        "tiempo_preparacion": 60,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Garbanzos", 150, "g"),
            ("Espinaca", 80, "g"),
            ("Tomate", 1, "unidad"),
            ("Zanahoria", 1, "unidad"),
        ],
    },
    {
        "nombre": "Pollo con arroz y zanahoria",
        "pasos": "Hervir el arroz en agua con una pizca de sal unos 15 minutos y escurrirlo. Pelar la zanahoria, cortarla en rodajas y hervirla 10 minutos. Cortar el pollo en trozos y salarlo. Calentar el aceite de oliva en una sartén a fuego medio. Cocinar el pollo 8 a 10 minutos, dándolo vuelta, hasta que no quede rosado por dentro. Servir el pollo con el arroz y la zanahoria.",
        "tiempo_preparacion": 40,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Pollo", 200, "g"),
            ("Arroz", 120, "g"),
            ("Zanahoria", 1, "unidad"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Hamburguesas de lentejas",
        "pasos": "Enjuagar las lentejas y hervirlas 20 a 25 minutos hasta que estén bien tiernas. Escurrirlas y pisarlas con un tenedor. Rallar la zanahoria. Mezclar las lentejas con la zanahoria y el huevo hasta formar una masa firme. Formar hamburguesas con las manos. Calentar el aceite en una sartén a fuego medio. Cocinar las hamburguesas 4 a 5 minutos de cada lado hasta que estén doradas.",
        "tiempo_preparacion": 45,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Lentejas", 150, "g"),
            ("Zanahoria", 1, "unidad"),
            ("Huevo", 1, "unidad"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Ensalada de camarones y tomate",
        "pasos": "Hervir los camarones en agua con sal 3 a 4 minutos hasta que estén rosados y bien cocidos. Escurrirlos y dejarlos enfriar. Lavar los tomates y cortarlos en cubos. Mezclar los camarones con el tomate. Condimentar con el aceite de oliva y servir.",
        "tiempo_preparacion": 20,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Camarón", 150, "g"),
            ("Tomate", 2, "unidad"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Revuelto de espinaca y queso",
        "pasos": "Lavar la espinaca y picarla. Cortar el queso en cubos chicos. Calentar el aceite de oliva en una sartén a fuego medio. Saltear la espinaca 2 minutos. Agregar los huevos batidos y el queso. Revolver 3 a 4 minutos hasta que el huevo esté bien cuajado.",
        "tiempo_preparacion": 15,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.CENA],
        "ingredientes": [
            ("Espinaca", 100, "g"),
            ("Huevo", 2, "unidad"),
            ("Queso", 40, "g"),
            ("Aceite de oliva", 5, "ml"),
        ],
    },
    {
        "nombre": "Yogur con frutillas y avena",
        "pasos": "Lavar las frutillas, quitarles el cabo y cortarlas en rodajas. Servir el yogur en un bowl. Agregar la avena y mezclar. Colocar las frutillas por encima.",
        "tiempo_preparacion": 5,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Yogur natural", 200, "g"),
            ("Frutilla", 100, "g"),
            ("Avena", 40, "g"),
        ],
    },
    {
        "nombre": "Ensalada de pera y naranja",
        "pasos": "Lavar la pera, quitarle el centro y cortarla en cubos. Pelar la naranja y cortarla en trozos. Mezclar las frutas en un bowl. Servir de inmediato.",
        "tiempo_preparacion": 10,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Pera", 1, "unidad"),
            ("Naranja", 1, "unidad"),
        ],
    },
    {
        "nombre": "Licuado de frutillas y banana",
        "pasos": "Lavar las frutillas y quitarles el cabo. Pelar la banana y cortarla en trozos. Colocar en la licuadora las frutillas, la banana y la leche. Licuar 30 segundos hasta que quede homogéneo. Servir de inmediato.",
        "tiempo_preparacion": 5,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Frutilla", 120, "g"),
            ("Banana", 1, "unidad"),
            ("Leche", 200, "ml"),
        ],
    },
    {
        "nombre": "Yogur con pera y almendras",
        "pasos": "Lavar la pera, quitarle el centro y cortarla en cubos. Picar las almendras. Servir el yogur en un bowl. Agregar la pera y espolvorear las almendras por encima.",
        "tiempo_preparacion": 5,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Yogur natural", 200, "g"),
            ("Pera", 1, "unidad"),
            ("Almendra", 20, "g"),
        ],
    },
    {
        "nombre": "Polenta con queso",
        "pasos": "Hervir agua con una pizca de sal en una olla. Bajar el fuego y agregar la harina de maíz en forma de lluvia, revolviendo sin parar para evitar grumos. Cocinar según las indicaciones del paquete, revolviendo seguido, hasta que espese. Rallar o cortar el queso en cubos. Agregar el queso, mezclar hasta que se derrita y servir caliente.",
        "tiempo_preparacion": 20,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Harina de maíz", 100, "g"),
            ("Queso", 50, "g"),
        ],
    },
    {
        "nombre": "Pollo al horno con batata",
        "pasos": "Precalentar el horno a 200 grados. Lavar la batata y cortarla en trozos medianos. Colocar la batata y el pollo en una fuente. Salar y rociar con el aceite de oliva. Hornear 35 a 40 minutos, dando vuelta todo a mitad de cocción. Verificar que el pollo no quede rosado por dentro y que la batata esté tierna.",
        "tiempo_preparacion": 50,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Pollo", 200, "g"),
            ("Batata", 200, "g"),
            ("Aceite de oliva", 15, "ml"),
        ],
    },
    {
        "nombre": "Ensalada de quinoa y verduras",
        "pasos": "Enjuagar la quinoa con agua fría en un colador. Hervirla en el doble de agua unos 12 a 15 minutos hasta que absorba el agua y escurrirla. Cortar el brócoli en ramitos y hervirlo 4 minutos. Cortar el tomate en cubos y rallar la zanahoria. Mezclar todo en un bowl y servir.",
        "tiempo_preparacion": 30,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Quinoa", 120, "g"),
            ("Brócoli", 100, "g"),
            ("Tomate", 1, "unidad"),
            ("Zanahoria", 1, "unidad"),
        ],
    },
    {
        "nombre": "Tortilla de papa y cebolla",
        "pasos": "Pelar la papa y cortarla en rodajas finas. Cortar la cebolla en tiras finas. Calentar el aceite en una sartén a fuego medio y cocinar la papa y la cebolla 12 a 15 minutos hasta que estén tiernas. Batir los huevos con una pizca de sal y mezclarlos con la papa y la cebolla. Cocinar la mezcla en la sartén 4 a 5 minutos. Dar vuelta la tortilla con ayuda de un plato y cocinar 4 minutos más.",
        "tiempo_preparacion": 35,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Papa", 200, "g"),
            ("Cebolla", 1, "unidad"),
            ("Huevo", 2, "unidad"),
            ("Aceite de oliva", 15, "ml"),
        ],
    },
    {
        "nombre": "Pure de zapallo con pollo",
        "pasos": "Pelar el zapallo y cortarlo en cubos. Hervirlo 15 a 20 minutos hasta que esté tierno y escurrirlo. Pisarlo con un tenedor hasta formar un puré. Salar el pollo. Calentar el aceite en una plancha o sartén a fuego medio. Cocinar el pollo 6 a 8 minutos de cada lado hasta que no quede rosado por dentro. Servir el pollo con el puré.",
        "tiempo_preparacion": 35,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Zapallo", 250, "g"),
            ("Pollo", 180, "g"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Merluza con papas y brocoli",
        "pasos": "Precalentar el horno a 200 grados. Pelar las papas, cortarlas en trozos y hervirlas 15 minutos. Cortar el brócoli en ramitos y hervirlo 4 minutos. Colocar la merluza en una fuente, salarla y rociarla con el aceite de oliva. Hornear 15 a 20 minutos hasta que se desarme fácilmente con el tenedor. Servir la merluza con las papas y el brócoli.",
        "tiempo_preparacion": 40,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Merluza", 200, "g"),
            ("Papa", 180, "g"),
            ("Brócoli", 100, "g"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },

    {
        "nombre": "Compota de manzana y pera",
        "pasos": "Pelar la manzana y la pera, quitarles el centro y cortarlas en cubos. Colocarlas en una olla con un chorrito de agua. Cocinar a fuego bajo 12 a 15 minutos hasta que estén tiernas. Pisarlas con un tenedor hasta obtener una compota. Dejar entibiar antes de servir.",
        "tiempo_preparacion": 20,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Manzana", 1, "unidad"),
            ("Pera", 1, "unidad"),
        ],
    },
    {
        "nombre": "Ensalada de naranja y frutillas",
        "pasos": "Pelar la naranja y cortarla en trozos. Lavar las frutillas, quitarles el cabo y cortarlas en rodajas. Mezclar las frutas en un bowl. Servir de inmediato.",
        "tiempo_preparacion": 10,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Naranja", 1, "unidad"),
            ("Frutilla", 150, "g"),
        ],
    },
    {
        "nombre": "Quinoa dulce con banana",
        "pasos": "Enjuagar la quinoa con agua fría en un colador. Hervirla en el doble de agua unos 12 a 15 minutos hasta que absorba el agua. Dejarla entibiar. Pisar la banana con un tenedor y mezclarla con la quinoa. Servir.",
        "tiempo_preparacion": 25,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Quinoa", 60, "g"),
            ("Banana", 1, "unidad"),
        ],
    },
    {
        "nombre": "Yogur con banana y frutillas",
        "pasos": "Pelar la banana y cortarla en rodajas. Lavar las frutillas, quitarles el cabo y cortarlas en rodajas. Servir el yogur en un bowl. Agregar la banana y las frutillas por encima.",
        "tiempo_preparacion": 5,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Yogur natural", 200, "g"),
            ("Banana", 1, "unidad"),
            ("Frutilla", 100, "g"),
        ],
    },
    {
        "nombre": "Porridge de avena y pera",
        "pasos": "Lavar la pera, quitarle el centro y cortarla en cubos. Calentar la leche en una olla a fuego medio. Agregar la avena y revolver 5 minutos hasta obtener una textura cremosa. Incorporar la pera y cocinar 1 minuto más. Servir caliente.",
        "tiempo_preparacion": 12,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Avena", 50, "g"),
            ("Leche", 200, "ml"),
            ("Pera", 1, "unidad"),
        ],
    },
    {
        "nombre": "Manzana asada con avena",
        "pasos": "Precalentar el horno a 180 grados. Lavar la manzana, cortarla por la mitad y retirar el centro. Colocar las mitades en una fuente con el corte hacia arriba. Cubrir con la avena. Hornear 20 minutos hasta que la manzana esté tierna.",
        "tiempo_preparacion": 25,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.DESAYUNO, TipoComida.MERIENDA],
        "ingredientes": [
            ("Manzana", 1, "unidad"),
            ("Avena", 40, "g"),
        ],
    },
    {
        "nombre": "Crema de zapallo y zanahoria",
        "pasos": "Pelar el zapallo, las zanahorias y la cebolla. Cortarlos en trozos medianos. Hervirlos en agua con una pizca de sal 20 minutos hasta que estén tiernos. Reservar un poco del agua de cocción y escurrir el resto. Procesar las verduras con un poco del agua reservada hasta obtener una crema. Servir caliente.",
        "tiempo_preparacion": 35,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Zapallo", 250, "g"),
            ("Zanahoria", 2, "unidad"),
            ("Cebolla", 1, "unidad"),
        ],
    },
    {
        "nombre": "Ensalada de quinoa y garbanzos",
        "pasos": "Enjuagar la quinoa y hervirla en el doble de agua unos 12 a 15 minutos. Si los garbanzos son secos, remojarlos desde la noche anterior y hervirlos hasta que estén tiernos. Si son de lata, escurrirlos y enjuagarlos. Cortar el tomate en cubos. Mezclar la quinoa, los garbanzos y el tomate. Condimentar con el aceite de oliva y servir.",
        "tiempo_preparacion": 35,
        "dificultad": NivelDificultad.PRINCIPIANTE,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Quinoa", 100, "g"),
            ("Garbanzos", 120, "g"),
            ("Tomate", 1, "unidad"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Batata rellena de lentejas",
        "pasos": "Precalentar el horno a 200 grados. Lavar la batata, pincharla con un tenedor y hornearla 35 a 40 minutos hasta que esté tierna. Mientras tanto, hervir las lentejas 20 a 25 minutos y escurrirlas. Picar la cebolla y saltearla en el aceite de oliva 5 minutos. Mezclar las lentejas con la cebolla. Abrir la batata al medio y rellenarla con la mezcla.",
        "tiempo_preparacion": 50,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Batata", 250, "g"),
            ("Lentejas", 120, "g"),
            ("Cebolla", 1, "unidad"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },
    {
        "nombre": "Salteado de pollo con brocoli y quinoa",
        "pasos": "Enjuagar la quinoa y hervirla en el doble de agua unos 12 a 15 minutos. Cortar el brócoli en ramitos y hervirlo 4 minutos. Cortar el pollo en trozos chicos y picar el ajo. Calentar el aceite de oliva en una sartén a fuego medio-alto. Cocinar el pollo con el ajo 8 a 10 minutos hasta que no quede rosado por dentro. Agregar el brócoli y saltear 2 minutos. Servir sobre la quinoa.",
        "tiempo_preparacion": 40,
        "dificultad": NivelDificultad.INTERMEDIO,
        "tipos_comida": [TipoComida.ALMUERZO, TipoComida.CENA],
        "ingredientes": [
            ("Pollo", 180, "g"),
            ("Brócoli", 150, "g"),
            ("Quinoa", 100, "g"),
            ("Ajo", 1, "unidad"),
            ("Aceite de oliva", 10, "ml"),
        ],
    },


]


def main():
    with SessionLocal() as db:
        ingredientes = {
            ingrediente.nombre: ingrediente.id
            for ingrediente in db.scalars(
                select(Ingrediente)
            ).all()
        }

        for datos in RECETAS_INICIALES:
            receta_existente = db.scalar(
                select(Receta).where(Receta.nombre == datos["nombre"])
            )

            # Si ya existe, completar porciones_base solo si falta
            # y actualizar los pasos si cambiaron.
            if receta_existente is not None:
                if receta_existente.porciones_base is None:
                    receta_existente.porciones_base = datos.get("porciones_base", 1)
                if receta_existente.pasos != datos["pasos"]:
                    receta_existente.pasos = datos["pasos"]
                continue

            for nombre, _, _ in datos["ingredientes"]:
                if nombre not in ingredientes:
                    raise ValueError(
                        f"Falta el ingrediente '{nombre}'. Ejecutá primero seed_catalogos."
                    )


            receta = Receta(
                nombre=datos["nombre"],
                pasos=datos["pasos"],
                tiempo_preparacion=datos["tiempo_preparacion"],
                dificultad=datos["dificultad"],
                porciones_base=datos.get("porciones_base", 1),
                info_nutricional=None,
                activa=True,
            )

            for tipo in datos["tipos_comida"]:
                receta.tipos_comida.append(
                    RecetaTipoComida(tipo_comida=tipo)
                )

            for nombre, cantidad, unidad in datos["ingredientes"]:
                receta.ingredientes.append(
                    RecetaIngrediente(
                        ingrediente_id=ingredientes[nombre],
                        cantidad=cantidad,
                        unidad=unidad,
                    )
                )

            db.add(receta)

        db.commit()


    print("Carga inicial de recetas finalizada.")


if __name__ == "__main__":
    main()
