
from sqlalchemy import select

from app.core.enums import NivelDificultad, TipoComida
from app.db.session import SessionLocal
from app.models.ingrediente import Ingrediente
from app.models.receta import Receta
from app.models.receta_ingrediente import RecetaIngrediente
from app.models.receta_tipo_comida import RecetaTipoComida


RECETAS_INICIALES = [
    {
        "nombre": "Avena con banana",
        "pasos": "Calentar la leche, agregar la avena y servir con banana cortada.",
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
        "pasos": "Cocinar el arroz. Cocinar el pollo con aceite de oliva y servir juntos.",
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
        "pasos": "Cocinar los garbanzos si es necesario. Cortar las verduras y mezclar.",
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
        "pasos": "Batir los huevos, agregar espinaca y queso, y cocinar en sartén.",
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
        "pasos": "Cocinar la merluza y acompañar con arroz hervido.",
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
        "pasos": "Cocinar la avena con leche y agregar manzana cortada.",
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
        "pasos": "Cortar la banana y acompañar con almendras.",
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
        "pasos": "Batir los huevos y cocinarlos en una sartén con tomate picado.",
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
        "pasos": "Procesar el maní hasta formar una pasta y servir con manzana cortada.",
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
        "pasos": "Batir los huevos, agregar queso y cocinar de ambos lados.",
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
        "pasos": "Cocinar las lentejas y mezclarlas con tomate y zanahoria.",
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
        "pasos": "Cocinar el pollo y acompañar con espinaca salteada.",
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
        "pasos": "Cocinar el arroz y las lentejas por separado y mezclarlos.",
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
        "pasos": "Mezclar los garbanzos cocidos con atun y tomate.",
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
        "pasos": "Cocinar la carne a la plancha y acompañar con zanahorias cocidas.",
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
        "pasos": "Cocinar la merluza al horno y acompañar con espinaca salteada.",
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
        "pasos": "Mezclar huevos con espinaca y cocinar en una sartén.",
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
        "pasos": "Cocinar el arroz, dejar enfriar y mezclar con atun y tomate.",
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
        "pasos": "Cortar la manzana y el queso y acompañar con almendras.",
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
        "pasos": "Licuar la banana con leche y avena hasta obtener una mezcla homogénea.",
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
        "pasos": "Cocinar la avena con leche durante unos minutos. Agregar banana en rodajas y almendras picadas.",
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
        "pasos": "Lavar y cortar la manzana. Licuarla con leche y avena hasta obtener una preparación homogénea.",
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
        "pasos": "Cortar la banana y la manzana en cubos. Agregar mani picado y mezclar.",
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
        "pasos": "Procesar el mani hasta formar una pasta. Mezclar con avena y banana pisada. Formar bolitas y refrigerar.",
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
        "pasos": "Cocinar el arroz. Cortar la carne en tiras y cocinarla completamente con aceite de oliva. Agregar tomate picado y servir con el arroz.",
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
        "pasos": "Cocinar los garbanzos previamente remojados hasta que estén tiernos. Incorporar tomate, zanahoria y espinaca. Cocinar hasta integrar los ingredientes.",
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
        "pasos": "Cocinar el arroz y las zanahorias. Cocinar completamente el pollo en una sartén con aceite de oliva y servir junto con las guarniciones.",
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
        "pasos": "Cocinar las lentejas hasta que estén tiernas. Pisarlas y mezclarlas con zanahoria rallada y huevo. Formar hamburguesas y cocinarlas completamente de ambos lados.",
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
        "pasos": "Cocinar completamente los camarones y dejarlos enfriar. Cortar el tomate, mezclar con los camarones y condimentar con aceite de oliva.",
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
        "pasos": "Lavar y saltear la espinaca. Incorporar los huevos batidos y el queso. Cocinar hasta que el huevo esté completamente cuajado.",
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
        "pasos": "Lavar y cortar las frutillas. Servir el yogur con avena y las frutas.",
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
        "pasos": "Lavar, pelar y cortar las frutas. Mezclar y servir.",
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
        "pasos": "Lavar las frutillas y licuarlas junto con la banana y la leche.",
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
        "pasos": "Cortar la pera y mezclarla con el yogur y las almendras picadas.",
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
        "pasos": "Hervir agua y agregar lentamente la harina de maíz mientras se mezcla. Cocinar según las indicaciones del producto y agregar queso.",
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
        "pasos": "Cortar la batata en trozos y colocarla en una fuente junto con el pollo. Agregar aceite de oliva y cocinar en horno precalentado hasta que ambos estén completamente cocidos.",
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
        "pasos": "Lavar y cocinar la quinoa. Cocinar el brócoli y mezclarlo con tomate, zanahoria y quinoa.",
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
        "pasos": "Cortar y cocinar la papa y la cebolla. Mezclar con los huevos batidos y cocinar la tortilla de ambos lados hasta que esté completamente cuajada.",
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
        "pasos": "Hervir el zapallo hasta que esté tierno y pisarlo. Cocinar completamente el pollo a la plancha y servir con el puré.",
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
        "pasos": "Cocinar la merluza al horno hasta que esté completamente cocida. Hervir las papas y el brócoli y servir como guarnición.",
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
        "pasos": "Pelar y cortar las frutas. Cocinarlas con un poco de agua hasta que estén tiernas y pisarlas hasta obtener una compota.",
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
        "pasos": "Pelar la naranja y cortarla en trozos. Lavar y cortar las frutillas. Mezclar y servir.",
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
        "pasos": "Lavar y cocinar la quinoa en agua hasta que esté tierna. Dejar entibiar y agregar banana pisada.",
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
        "pasos": "Cortar la banana y las frutillas. Mezclarlas con el yogur natural y servir.",
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
        "pasos": "Cocinar la avena con leche hasta obtener una textura cremosa. Agregar la pera cortada en cubos.",
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
        "pasos": "Cortar la manzana en mitades y retirar las semillas. Agregar avena por encima y hornear hasta que la fruta esté tierna.",
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
        "pasos": "Cortar el zapallo, la zanahoria y la cebolla. Hervir hasta que estén tiernos y procesar hasta obtener una crema homogénea.",
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
        "pasos": "Cocinar la quinoa y los garbanzos hasta que estén tiernos. Mezclar con tomate y aceite de oliva.",
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
        "pasos": "Hornear la batata hasta que esté tierna. Cocinar las lentejas y mezclarlas con cebolla salteada. Abrir la batata y rellenar.",
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
        "pasos": "Cocinar la quinoa y el brócoli. Cortar el pollo en trozos y cocinarlo completamente con aceite de oliva y ajo. Incorporar las verduras y servir con la quinoa.",
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

            # Si ya existe, completar porciones_base solo si falta.
            if receta_existente is not None:
                if receta_existente.porciones_base is None:
                    receta_existente.porciones_base = datos.get("porciones_base", 1)
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
