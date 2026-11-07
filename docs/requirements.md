# NutriPlanner — Documentación de requisitos

**Especificación de requisitos — Demo académica implementada y MVP proyectado**  
**Versión 3.0 | Noviembre de 2026**

> **Alcance de esta entrega:** la versión implementada y presentada en Programación II es la **DEMO funcional**. El **MVP proyectado** corresponde a la siguiente etapa y todavía no debe describirse como completamente implementado. Las capacidades comerciales y las extensiones opcionales se documentan por separado.

**Estados empleados:** `DEMO — implementado`, `DEMO — parcial/limitado`, `MVP — pendiente`, `MVP — opcional`, `POST-MVP — futuro`. La clasificación se basa en lo existente en el código integrado en `main` al cierre de la demo; las pruebas manuales no equivalen a una auditoría exhaustiva en producción.

> NutriPlanner es una plataforma de planificación alimentaria que filtra recetas precargadas según las restricciones alimentarias y el nivel culinario del usuario, y permite organizar menús personalizados.

---

## Índice

0. [Etapas de desarrollo y alcance de entrega](#0-etapas-de-desarrollo-y-alcance-de-entrega)
1. [Idea de negocio](#1-idea-de-negocio)
2. [Requerimientos de alto nivel](#2-requerimientos-de-alto-nivel)
3. [Requerimientos funcionales](#3-requerimientos-funcionales)
4. [Reglas de negocio](#4-reglas-de-negocio)
5. [Requerimientos no funcionales](#5-requerimientos-no-funcionales)
6. [Casos de uso](#6-casos-de-uso)
7. [Trazabilidad de la demo y criterios de aceptación](#7-trazabilidad-de-la-demo-y-criterios-de-aceptacion)

---

## 0. Etapas de desarrollo y alcance de entrega

Este documento distingue **lo que el equipo mostrará en la defensa** de lo que propone terminar como producto mínimo y de las funcionalidades de evolución. **Una demo funcional no implica que todas las funciones del MVP estén terminadas**.

| Etapa | Propósito | Estado |
| --- | --- | --- |
| **DEMO académica — entrega actual** | Mostrar un recorrido completo y verificable: registrarse, configurar perfil, consultar recetas, generar, sustituir y guardar un menú; revisar el historial y eliminar un menú. | Implementada, con limitaciones explícitas. |
| **MVP proyectado — próxima iteración** | Completar la propuesta mínima de producto definida por el equipo: reutilización de menús; calificaciones y valoraciones; reportes y moderación, con las reglas asociadas. | Pendiente de implementación. |
| **MVP opcional / secundario** | Exportar a PDF, recuperar contraseña y eliminar cuenta. | Pendiente; sujeto a prioridades. |
| **POST-MVP** | Profesionales, integración comercial, funciones clínicas, lista de compras, monetización y servicios externos. | Fuera de la entrega y del MVP inicial. |

### 0.1 Evidencia técnica de la DEMO

- **Frontend:** React / TypeScript, integrado en `sxlvtti/nutriplanner-front`, rama `main`, desplegado en Render.
- **API:** Python / FastAPI, integrada en `KarenGonzalesCh/nutriplanner-api`, rama `main`, desplegada en Render.
- **Persistencia:** SQLAlchemy y Alembic; desarrollo local con SQLite y despliegue con PostgreSQL. La base PostgreSQL está configurada externamente; la migración de menús fue observada en los registros de Render.
- **Seguridad:** autenticación JWT; contraseñas almacenadas con Argon2.
- **Patrón de diseño:** Strategy para la evaluación de restricciones alimentarias.
- **Pruebas disponibles al cierre de esta documentación:** 198 pruebas aprobadas de backend y 1 prueba aprobada de frontend. La prueba del frontend es de enrutamiento; no constituye cobertura automatizada integral del flujo de menús.

### 0.2 Límites concretos de la DEMO

- La generación admite **1 a 7 días** y los tipos desayuno, almuerzo, merienda y cena. El frontend actual envía **1 comensal** y tamaño de porción **NORMAL**, aunque la API admite más comensales para este tamaño.
- La generación produce una **propuesta temporal**; el guardado es una operación separada y exige validar todas las comidas y sustituciones requeridas.
- El reemplazo de recetas se inicia en el frontend y se **revalida en la API al guardar**. No se debe describir como un motor autónomo de reemplazos persistentes.
- La **sustitución persistente por receta** se permite para ingredientes restringidos; la **sustitución guardada en un menú** queda asociada a una comida concreta y no altera el catálogo.
- El menú guardado conserva una **instantánea histórica** de receta, preparación, ingredientes, cantidades y alternativas confirmadas. **No existe aún un flujo de reutilización editable** de ese menú.
- Las calificaciones, reportes, permisos de moderación y operaciones administrativas **no forman parte de la demo implementada**.
- El filtrado por incompatibilidad del listado de recetas no es idéntico a consultar el estado de compatibilidad de una receta: el detalle puede informar **COMPATIBLE, ADAPTABLE o INCOMPATIBLE**; la visualización integral de todas las adaptables en el listado personalizado queda por revisar.

---

## 1. Idea de negocio

NutriPlanner es una plataforma de planificación alimentaria que permite generar menús personalizados orientados a una alimentación saludable a partir de las alergias, los alimentos o ingredientes específicos y las categorías de alimentos que el usuario no consume o desea evitar, y su nivel culinario.

El sistema parte de una base de recetas precargada y previamente definida para la demo, extensible en el MVP. Cada receta contiene sus ingredientes, cantidades, uno o más tipos de comida, nivel de dificultad, información nutricional precargada y, cuando corresponda, alternativas previamente establecidas para determinados ingredientes.

Ni la demo ni el MVP inicial calculan automáticamente si una receta es saludable o los valores nutricionales. Las recetas disponibles forman parte de un catálogo precargado y previamente seleccionado para el proyecto, y la información nutricional que se muestra es un dato informativo precargado en dicho catálogo. La personalización realizada por NutriPlanner consiste en filtrar y organizar las recetas según las restricciones alimentarias y el nivel culinario del usuario.

A partir del perfil del usuario, NutriPlanner filtra las recetas disponibles y genera propuestas de menú evitando los ingredientes restringidos por las alergias declaradas o por los alimentos que el usuario haya indicado que no desea consumir. Una receta con ingredientes restringidos solo se ofrece cuando existe una alternativa previamente definida, que el usuario debe seleccionar para poder incorporarla a su menú.

**Problema que resuelve:** una persona puede querer alimentarse de manera más organizada o evitar determinados alimentos, pero eso no necesariamente le resuelve qué cocinar, qué recetas respetan sus restricciones alimentarias, qué alternativas puede utilizar para determinados ingredientes ni cómo organizar varios días de comidas sin repetir siempre lo mismo. NutriPlanner busca simplificar esa planificación ofreciendo recetas y menús personalizados a partir de la información proporcionada por el usuario.

### 1.1 Actores de la demo y del MVP proyectado

**Usuario**

Es el actor principal de la plataforma. Las funciones enunciadas se distinguen por etapa; en la demo ya puede:

- registrarse y autenticarse;
- gestionar su perfil alimentario;
- declarar alergias;
- indicar alimentos o ingredientes específicos y categorías de alimentos que no consume o desea evitar;
- indicar su nivel culinario;
- consultar recetas;
- consultar alternativas disponibles para determinados ingredientes;
- seleccionar alternativas de ingredientes cuando corresponda;
- recibir sugerencias de recetas;
- generar menús;
- reemplazar recetas dentro de un menú;
- guardar y consultar menús;
- gestionar recetas favoritas y excluidas;
- eliminar los menús de su propia cuenta;
- consultar el historial de menús con las sustituciones confirmadas;
- guardar y quitar preferencias de sustitución de recetas restringidas.

**En el MVP proyectado**, el Usuario además podrá reutilizar menús guardados, calificar recetas de 1 a 5 estrellas y reportar recetas cuando detecte inconvenientes.

**Administrador/Moderador — actor previsto para el MVP, no incluido en la demo**

Será un actor interno autorizado encargado de gestionar los reportes realizados por los usuarios. Puede:

- consultar los reportes, filtrándolos por estado (pendiente, cerrado o aceptado);
- consultar el detalle de un reporte;
- cerrar un reporte cuando determine que no requiere acciones adicionales;
- aceptar un reporte cuando considere que requiere revisión;
- desactivar preventivamente una receta asociada a un reporte aceptado.

El Administrador/Moderador no crea ni modifica recetas, ingredientes, sustituciones ni información nutricional, y no reactiva recetas desactivadas. Tampoco realiza validaciones profesionales sobre el contenido alimentario.

### 1.2 Alcance de la DEMO académica (implementado)

El equipo presentará una versión de extremo a extremo con:

- registro y autenticación de usuarios;
- gestión del perfil alimentario;
- registro de alergias;
- registro de alimentos o ingredientes específicos y categorías de alimentos que el usuario no consume o desea evitar;
- selección del nivel culinario;
- consulta de recetas precargadas;
- filtrado de recetas según el perfil del usuario;
- sugerencias de recetas;
- generación de menús para períodos de entre 1 y 7 días;
- utilización de los tipos de comida desayuno, almuerzo, merienda y cena;
- reemplazo de recetas dentro de un menú;
- guardado, consulta histórica y eliminación de menús propios;
- gestión de recetas favoritas y excluidas;
- consulta y selección de alternativas precargadas para determinados ingredientes;
- conservación de las sustituciones elegidas dentro del menú correspondiente;
- conservación de instantáneas históricas y de alternativas confirmadas por comida;
- consulta, guardado y eliminación de preferencias de sustitución de ingredientes restringidos;
- despliegue de frontend y API en Render y persistencia relacional.

**Límites de la demo:** sin reutilización editable, calificaciones, reportes ni moderación. La interfaz de generación utiliza un comensal y tamaño de porción normal.

### 1.3 Alcance del MVP proyectado (pendiente)

El MVP contempla **todo lo ya implementado en la demo**, más las funciones previstas originalmente en esta especificación que aún faltan:

- reutilización de menús guardados, con revalidación del perfil y de las alternativas y sin alterar el menú histórico;
- calificaciones de recetas (1 a 5 estrellas), mantenimiento de una calificación vigente y cálculo del promedio;
- reporte de recetas por parte de los usuarios y reglas de exclusión temporal por reporte pendiente;
- autenticación/autorización del Administrador/Moderador;
- consulta, cierre y aceptación de reportes y desactivación preventiva de recetas;
- mejoras en la oferta visible de recetas adaptables y en los controles y mensajes del flujo completo.

**Estos requerimientos no están implementados y no deben presentarse como funcionalidades disponibles en la demo.**

### 1.4 Funcionalidades deseables o secundarias del MVP (no implementadas)

Las siguientes funcionalidades podrán incorporarse al MVP si el alcance y los tiempos de implementación lo permiten:

- **Exportación de menús a PDF** (prioridad: deseable).
- **Recuperación de contraseña** (prioridad: secundaria).
- **Eliminación de cuenta y de los datos personales asociados** (prioridad: secundaria).

### 1.5 Fuera de alcance del MVP (visión futura)

Incorporación de profesionales, lista de compras, comercios, publicidad, geolocalización, marketplace, obras sociales/prepagas, diagnóstico o prescripción médica, cálculo de calorías/macronutrientes y reactivación de recetas desactivadas.

### 1.6 Plan de monetización

El modelo de monetización corresponde a una evolución comercial posterior al MVP. Por lo tanto, ni la demo académica ni el MVP proyectado contemplan la implementación de pagos, suscripciones ni publicidad.

En una futura etapa comercial, NutriPlanner adoptaría un modelo freemium. El plan gratuito permitiría utilizar las funcionalidades principales de la plataforma y podría financiarse parcialmente mediante publicidad no invasiva. El plan Premium se plantea como una suscripción mensual o anual que ofrecería funcionalidades avanzadas y una experiencia sin publicidad.

| **Plan** | **Características previstas**                                                                                           | **Modalidad**               |
| -------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| Gratuito | Consulta de recetas, generación básica de menús y funcionalidades principales de planificación                          | Publicidad no invasiva      |
| Premium  | Mayor personalización, historial y reutilización ampliada de menús, herramientas avanzadas y experiencia sin publicidad | Suscripción mensual o anual |

El objetivo del plan gratuito sería permitir que el usuario conozca y utilice el servicio sin realizar un pago inicial. El plan Premium constituiría la principal fuente de ingresos prevista, mientras que la publicidad contribuiría al sostenimiento de los costos asociados a los usuarios gratuitos.


```text
                     [ DEMO ]

  Versión académica implementada y demostrable

                        │

                        ▼

                     [ MVP ]

  Completar reutilización, calificaciones y moderación

                        │

                        ▼

              [ EVOLUCIÓN COMERCIAL ]

                        │

          ┌─────────────┴─────────────┐

          ▼                           ▼

     [ GRATUITO ]                [ PREMIUM ]

          │                           │

  Funciones básicas           Funciones avanzadas

          │                           │

      Publicidad             Suscripción mensual/anual

          │                           │

     Con anuncios               Sin publicidad
```

## 2. Requerimientos de alto nivel

**RQ1 — Gestión de cuenta:** [DEMO para usuarios; MVP para moderación] El usuario podrá registrarse y autenticarse para acceder a las funcionalidades asociadas a su cuenta. En el MVP proyectado, los usuarios internos autorizados podrán autenticarse para acceder a las funciones de moderación.

**RQ2 — Gestión del perfil alimentario:** [DEMO] el usuario podrá configurar y modificar sus alergias alimentarias, los alimentos o ingredientes específicos y las categorías de alimentos que no consume o desea evitar, y su nivel culinario.

**RQ3 — Consulta personalizada de recetas:** [DEMO] el usuario podrá consultar recetas adecuadas a su perfil, acceder a su detalle y conocer las alternativas disponibles para determinados ingredientes.

**RQ4 — Generación de menús:** [DEMO] el usuario podrá recibir sugerencias y generar menús personalizados para períodos de hasta siete días, utilizando desayuno, almuerzo, merienda y cena como tipos de comida.

**RQ5 — Gestión de menús:** [DEMO parcial; MVP para reutilización] El usuario podrá reemplazar recetas, guardar menús, consultar su historial y eliminar menús propios. Reutilizar menús anteriores como base editable queda previsto para el MVP.

**RQ6 — Personalización de recetas:** [DEMO] el usuario podrá seleccionar alternativas previamente definidas para determinados ingredientes cuando una receta las contemple.

**RQ7 — Gestión de favoritas, exclusiones y calificaciones:** [DEMO para favoritas/exclusiones; MVP para calificaciones] El usuario podrá marcar recetas como favoritas, excluirlas y, en el MVP, calificarlas mediante una puntuación de 1 a 5 estrellas.

**RQ8 — Reporte y moderación de recetas:** [MVP pendiente] El usuario podrá reportar recetas en las que detecte algún inconveniente, y el Administrador/Moderador podrá consultar, cerrar o aceptar esos reportes y desactivar preventivamente las recetas asociadas a reportes aceptados.

**RQ9 — Exportación:** [MVP opcional] El usuario podrá exportar sus menús a PDF.

*Prioridad: deseable.*

**RQ10 — Gestión avanzada de la cuenta:** [MVP opcional] El usuario podrá restablecer su contraseña y eliminar su cuenta y los datos personales asociados.

*Prioridad: secundaria / sujeta al alcance del MVP.*

### 2.1 Trazabilidad de alto nivel por etapa

| Requerimiento | DEMO presentada | MVP posterior |
| --- | --- | --- |
| RQ1 | Registro, sesión y acceso propio | Autenticación y permisos de moderación |
| RQ2 | Perfil alimentario | Mejoras y refinamientos |
| RQ3 | Recetas y detalle de compatibilidad | Mejoras de catálogo y descubrimiento de adaptables |
| RQ4 | Generación 1–7 días | Refinamientos del generador |
| RQ5 | Reemplazo previo al guardado, guardado, historial y eliminación | Reutilización editable con revalidación |
| RQ6 | Sustituciones en menú y preferencias por receta | Extensión de opciones y UX |
| RQ7 | Favoritas y exclusiones | Calificaciones y promedio |
| RQ8 | — | Reportes y moderación |
| RQ9 | — | Exportación PDF opcional |
| RQ10 | — | Recuperación de contraseña y eliminación de cuenta opcionales |

## 3. Requerimientos funcionales

### 3.1 Autenticación y cuenta

**RF1.** `[DEMO — implementado]` El sistema debe permitir al usuario registrarse proporcionando los datos obligatorios de la cuenta, incluyendo correo electrónico, nombre de usuario y contraseña.

**RF2.** `[DEMO — implementado]` El sistema debe permitir al usuario autenticarse mediante sus credenciales registradas para acceder a las funcionalidades asociadas a su cuenta.

**RF3.** `[MVP — pendiente]` El sistema debe permitir al Administrador/Moderador autenticarse mediante una cuenta interna autorizada (ver RN21).

**RF4.** `[MVP — pendiente]` El sistema debe restringir las funcionalidades disponibles de acuerdo con el rol autenticado, diferenciando las funciones del Usuario de las funciones del Administrador/Moderador.

**RF5.** `[MVP — opcional]` El sistema debe permitir al usuario solicitar el restablecimiento de su contraseña cuando no pueda acceder a su cuenta.

**RF6.** `[MVP — opcional]` El sistema debe permitir al usuario autenticado eliminar su cuenta y los datos personales asociados, según lo dispuesto en RN20.

*Prioridad de RF5 y RF6: secundaria / sujeta al alcance del MVP.*

### 3.2 Perfil alimentario

**RF7.** `[DEMO — implementado]` El sistema debe permitir al usuario indicar sus alergias alimentarias a partir de un catálogo predefinido.

**RF8.** `[DEMO — implementado]` El sistema debe permitir al usuario seleccionar alimentos o ingredientes específicos y categorías de alimentos que no consume o desea evitar, a partir de los catálogos definidos por el sistema.

**RF9.** `[DEMO — implementado]` El sistema debe permitir al usuario indicar su nivel culinario.

**RF10.** `[DEMO — implementado]` El sistema debe almacenar el perfil alimentario del usuario y permitir su modificación.

### 3.3 Filtrado y personalización de recetas

**RF11.** `[DEMO — implementado]` El sistema debe considerar las restricciones del perfil alimentario (alergias, alimentos o ingredientes específicos y categorías de alimentos a evitar) al determinar las recetas que puede ofrecerle al usuario.

**RF12.** `[DEMO — implementado]` El sistema debe considerar restringidos los alimentos o ingredientes asociados a una alergia declarada por el usuario, sin aplicar niveles intermedios de restricción o priorización. Una receta que contenga un ingrediente restringido por alergia solo podrá ofrecerse si existe una alternativa válida previamente definida para dicho ingrediente, en cuyo caso deberá indicarse que requiere sustitución.

**RF13.** `[DEMO — parcial]` Cuando una receta contenga uno o más ingredientes restringidos por el perfil del usuario, el sistema solo podrá ofrecerla si existe una alternativa válida previamente definida para cada uno de ellos. Si para alguno no existe una alternativa válida, la receta no deberá ser sugerida ni incluida en un menú; podrá seguir siendo consultada explícitamente para informar incompatibilidad.

**RF14.** `[DEMO — implementado]` El sistema debe utilizar el nivel culinario del usuario para personalizar las recetas que le sugiere automáticamente, según la correspondencia definida en RN3.

### 3.4 Generación de menús

**RF15.** `[DEMO — parcial]` El sistema debe permitir al usuario seleccionar un tipo de comida entre desayuno, almuerzo, merienda y cena y mostrarle hasta una cantidad máxima de recetas disponibles definida por el sistema.

**RF16.** `[DEMO — implementado]` El sistema debe permitir al usuario generar un menú diario seleccionando las comidas que desea incluir.

**RF17.** `[DEMO — implementado]` El sistema debe permitir al usuario generar un menú para un período de entre 2 y 7 días, seleccionando las comidas que desea incluir en cada día.

**RF18.** `[DEMO — implementado]` El sistema debe permitir visualizar el menú generado, mostrando los días seleccionados, las comidas incluidas y la receta asignada a cada una.

**RF19.** `[DEMO — implementado]` El sistema debe evitar repetir una misma receta dentro del período generado mientras existan otras recetas disponibles suficientes.

**RF20.** `[DEMO — implementado]` El sistema debe informar al usuario cuando no existan recetas disponibles para una comida solicitada que respeten las restricciones definidas en su perfil.

**RF21.** `[DEMO — implementado]` El sistema debe excluir de las sugerencias y menús las recetas que el usuario haya marcado como excluidas (ver RN19).

### 3.5 Reemplazo de recetas en un menú

**RF22.** `[DEMO — implementado]` El sistema debe permitir al usuario reemplazar una receta puntual de un menú generado.

**RF23.** `[DEMO — parcial]` El sistema debe ofrecer como reemplazo otras recetas disponibles y diferentes de la receta actual, siempre que existan opciones. El reemplazo elegido en la interfaz es provisional y deberá superar la validación del backend antes de guardar el menú.

**RF24.** `[DEMO — implementado]` El sistema debe mantener sin cambios el resto del menú cuando se reemplace una receta.

### 3.6 Guardado de menús

**RF25.** `[DEMO — implementado]` El sistema debe permitir al usuario guardar un menú generado, asociándolo a su cuenta para poder consultarlo posteriormente, siempre que no contenga recetas pendientes de sustitución (RF56) ni posiciones seleccionadas sin confirmar.

**RF59.** `[DEMO — implementado]` Al guardar un menú, el sistema debe conservar para cada comida una instantánea con la receta, los pasos, los ingredientes, cantidades, unidades y sustituciones confirmadas, sin modificar el catálogo.

**RF62.** `[DEMO — implementado]` El sistema debe verificar que el conjunto de comidas confirmadas coincida con las posiciones de comida seleccionadas y que haya al menos una comida confirmada para cada día configurado.

### 3.7 Consulta y reutilización de menús guardados

**RF26.** `[DEMO — implementado]` El sistema debe mostrar al usuario el historial de sus menús guardados.

**RF27.** `[DEMO — implementado]` El sistema debe permitir al usuario consultar el detalle de un menú guardado.

**RF58.** `[DEMO — implementado]` El sistema debe permitir al usuario eliminar un menú guardado que pertenezca a su cuenta, previa confirmación de la acción.

**RF61.** `[DEMO — implementado]` El sistema debe impedir el acceso al detalle o eliminación de un menú que no pertenezca al usuario autenticado.

**RF28.** `[MVP — pendiente]` El sistema debe permitir al usuario reutilizar un menú guardado como base para un nuevo menú, conservando inicialmente las recetas que lo componen, sujetas a la revalidación definida en RN7 y RF57, y permitiendo realizar reemplazos, sin modificar el menú guardado original.

**RF57.** `[MVP — pendiente]` Al reutilizar un menú guardado, el sistema debe revalidar cada receta y sustitución según el perfil actual del usuario y el estado actual de las recetas. Toda receta que ya no sea válida debe marcarse como no disponible, y el usuario deberá reemplazarla antes de guardar el nuevo menú. Toda receta cuya sustitución ya no sea válida debe quedar pendiente de sustitución (RF56).

### 3.8 Consulta de recetas

**RF29.** `[DEMO — parcial]` El sistema debe permitir consultar recetas sin limitar la exploración manual por nivel culinario. La lista personalizada predeterminada filtra recetas compatibles; la consulta de compatibilidad de una receta permite distinguir COMPATIBLE, ADAPTABLE (con sustituciones válidas) e INCOMPATIBLE. La inclusión uniforme de las adaptables en el listado personalizado requiere mejoras de integración.

**RF30.** `[DEMO — implementado]` El sistema debe mostrar el detalle de una receta, incluyendo:

- ingredientes;
- cantidades;
- pasos de preparación;
- tiempo de preparación;
- nivel de dificultad;
- uno o más tipos de comida asociados;
- información nutricional precargada (dato informativo del catálogo; el sistema no la calcula);
- alternativas disponibles para determinados ingredientes, cuando existan.

**RF31.** `[DEMO — implementado]` El sistema debe indicar en el detalle de una receta cuáles de sus ingredientes admiten alternativas previamente definidas.

### 3.9 Alternativas de ingredientes

**RF32.** `[DEMO — implementado]` El sistema debe permitir al usuario consultar las alternativas previamente definidas para un ingrediente de una receta cuando estas existan.

**RF33.** `[DEMO — implementado]` El sistema debe impedir que se ofrezca como alternativa un ingrediente que entre en conflicto con las restricciones del perfil alimentario del usuario.

**RF34.** `[DEMO — implementado]` El sistema debe permitir al usuario seleccionar una alternativa válida para sustituir un ingrediente dentro de una receta, tanto durante la confirmación de una comida como, cuando el ingrediente esté restringido, para guardar una preferencia personal por receta.

**RF35.** `[DEMO — implementado]` La selección de una alternativa no debe modificar la receta original almacenada en el catálogo.

**RF36.** `[DEMO — implementado]` Cuando una receta forme parte de un menú, el sistema debe conservar la alternativa seleccionada por el usuario asociada a esa receta dentro de dicho menú.

**RF56.** `[DEMO — implementado]` Cuando un menú generado, o el reemplazo de una receta, incluya una receta con ingredientes restringidos que cuenten con alternativa válida, el sistema debe marcar la receta como pendiente de sustitución y solicitar al usuario que seleccione una alternativa para cada ingrediente restringido. El sistema no debe permitir guardar un menú que contenga recetas pendientes de sustitución.

**RF60.** `[DEMO — implementado]` El sistema debe permitir consultar, guardar y quitar una preferencia de sustitución de un ingrediente **restringido** en una receta concreta, asociándola al usuario; la alternativa deberá pertenecer a esa posición de la receta y ser compatible con el perfil vigente.

### 3.10 Favoritas y exclusiones

**RF37.** `[DEMO — parcial]` El sistema debe permitir al usuario marcar una receta como favorita desde las pantallas que dispongan de esa acción y conservar la preferencia en el backend.

**RF38.** `[DEMO — implementado]` El sistema debe permitir al usuario consultar sus recetas favoritas.

**RF39.** `[DEMO — implementado]` El sistema debe permitir al usuario quitar una receta de sus favoritas.

**RF40.** `[DEMO — parcial]` El sistema debe permitir al usuario excluir una receta para que no sea incluida automáticamente en nuevas sugerencias y menús. La exclusión no implica necesariamente ocultar su consulta manual desde el catálogo (ver RN19).

**RF41.** `[DEMO — implementado]` El sistema debe permitir al usuario quitar una receta de sus exclusiones, habilitando nuevamente su aparición cuando resulte adecuada a su perfil.

### 3.11 Calificación de recetas

**RF42.** `[MVP — pendiente]` El sistema debe permitir al usuario calificar una receta mediante una puntuación de 1 a 5 estrellas.

**RF43.** `[MVP — pendiente]` El sistema debe permitir al usuario modificar la calificación que haya otorgado previamente a una receta.

**RF44.** `[MVP — pendiente]` El sistema debe mantener una única calificación vigente por usuario y receta.

**RF45.** `[MVP — pendiente]` El sistema debe calcular y mostrar la calificación promedio de una receta a partir de las valoraciones realizadas por los usuarios.

**Resumen de funciones sobre recetas**

| **Función** | **Para qué sirve**                               |
| ----------- | ------------------------------------------------ |
| Favorita    | Guardar una receta que quiero volver a consultar |
| Excluir     | No quiero que esa receta vuelva a aparecer       |
| Calificar   | Expresar cuánto me gustó mediante 1–5 estrellas  |

### 3.12 Reporte y moderación de recetas

**RF46.** `[MVP — pendiente]` El sistema debe permitir al usuario reportar una receta seleccionando un motivo de un catálogo predefinido y pudiendo agregar un comentario opcional.

**RF47.** `[MVP — pendiente]` El sistema debe registrar el reporte asociándolo al usuario, la receta, el motivo, el comentario opcional y su estado.

**RF48.** `[MVP — pendiente]` El sistema debe impedir que un usuario tenga más de un reporte pendiente sobre la misma receta.

**RF49.** `[MVP — pendiente]` Mientras exista un reporte pendiente realizado por un usuario sobre una receta, el sistema debe excluir dicha receta de las nuevas sugerencias y menús de ese usuario (ver RN19).

**RF50.** `[MVP — pendiente]` El sistema debe permitir al Administrador/Moderador consultar los reportes, pudiendo filtrarlos por estado (pendiente, cerrado o aceptado). Por defecto se muestran los reportes pendientes.

**RF51.** `[MVP — pendiente]` El sistema debe permitir al Administrador/Moderador consultar el detalle de un reporte.

**RF52.** `[MVP — pendiente]` El sistema debe permitir al Administrador/Moderador cerrar un reporte cuando no requiera acciones adicionales.

**RF53.** `[MVP — pendiente]` El sistema debe permitir al Administrador/Moderador aceptar un reporte y desactivar preventivamente la receta asociada.

**RF54.** `[MVP — pendiente]` El sistema debe impedir que una receta desactivada aparezca en nuevas sugerencias, menús o listados para cualquier usuario (ver RN19).

### 3.13 Exportación

**RF55.** `[MVP — opcional]` El sistema debe permitir al usuario exportar a PDF un menú generado o guardado, incluyendo las comidas y recetas que lo componen.

*Prioridad: deseable.*

## 4. Reglas de negocio

### 4.1 Restricciones del perfil alimentario

En este documento se denominan **restricciones del perfil alimentario** al conjunto formado por las alergias declaradas, los alimentos o ingredientes específicos y las categorías de alimentos que el usuario no consume o desea evitar.

**RN1 — Alergias:** `[DEMO — implementado]` los alimentos o ingredientes asociados a una alergia declarada por el usuario deben considerarse restringidos. La restricción es obligatoria: el sistema no debe moderar ni priorizar su aparición. Una receta que contenga un ingrediente restringido por alergia solo podrá ofrecerse cuando exista una alternativa válida previamente definida, quedando pendiente de sustitución hasta que el usuario seleccione dicha alternativa. 

**RN2 — Alimentos, ingredientes y categorías a evitar:** `[DEMO — implementado]` cuando el usuario indique que no consume o desea evitar un alimento o ingrediente específico, ese ingrediente se considerará restringido. Cuando indique una categoría de alimentos, se considerarán restringidos todos los ingredientes pertenecientes a dicha categoría.

### 4.2 Nivel culinario

**RN3 — Nivel culinario:** `[DEMO — implementado]` para las sugerencias automáticas de recetas se aplicará la siguiente correspondencia:

| **Nivel del usuario** | **Niveles de recetas sugeridos**    |
| --------------------- | ----------------------------------- |
| Principiante          | Principiante                        |
| Intermedio            | Principiante e Intermedio           |
| Avanzado              | Principiante, Intermedio y Avanzado |

El nivel culinario no impedirá que el usuario consulte manualmente recetas de otros niveles desde el catálogo.

### 4.3 Alternativas de ingredientes

**RN4 — Sustitución obligatoria:** `[DEMO — implementado]` cuando una receta contenga un ingrediente restringido por el perfil del usuario y exista una alternativa válida, la receta se considera pendiente de sustitución. El usuario deberá seleccionar una alternativa antes de poder guardar el menú que la contiene. Si la receta contiene varios ingredientes restringidos, debe existir y seleccionarse una alternativa válida para cada uno; si para alguno no existe, la receta no se ofrece.

Ejemplo:

Usuario evita: azúcar

Receta:        azúcar (restringido)

Alternativas:  miel ✓   otro endulzante ✓

→ la receta queda pendiente de sustitución

→ el usuario debe elegir una alternativa para poder guardar el menú

**RN5 — Sustitución opcional:** `[DEMO — parcial]` cuando el ingrediente original no esté restringido, el usuario podrá conservarlo. En el guardado de un menú, la API admite una alternativa voluntaria siempre que esté previamente definida para la posición de la receta y sea compatible. **La pantalla para guardar preferencias persistentes por receta solo admite sustituciones de ingredientes restringidos**; la experiencia completa de alternativas voluntarias queda para mejorar en el MVP.

**RN6 — Persistencia de la sustitución:** `[DEMO — implementado]` la alternativa elegida debe almacenarse de forma específica en la comida del menú confirmado y no debe modificar la receta original del catálogo. Además, la demo permite persistir separadamente preferencias por usuario y posición de ingrediente en una receta; ambos registros tienen propósitos distintos.

### 4.4 Reutilización de menús

**RN7 — Revalidación del menú:** `[MVP — pendiente]` al reutilizar un menú guardado, el sistema deberá volver a verificar sus recetas y sustituciones según las restricciones actuales del perfil del usuario y el estado actual de las recetas. Las recetas que ya no sean válidas se marcarán como no disponibles y deberán reemplazarse antes de guardar el nuevo menú; las sustituciones que ya no sean válidas dejarán la receta pendiente de sustitución. El menú histórico original permanecerá sin modificaciones.

Ejemplo:

Menú antiguo:  Pizza con queso

Después el usuario agrega:  Evitar → Lácteos

Al reutilizar el menú:

→ la receta se verifica de nuevo

→ si no existe alternativa válida, se marca como no disponible y debe reemplazarse

Menú histórico:

→ permanece intacto

### 4.5 Favoritas y exclusiones

**RN8 — Prioridad de la exclusión:** `[DEMO — implementado]` si una misma receta se encuentra simultáneamente marcada como favorita y excluida, la exclusión tendrá prioridad. La receta podrá mantenerse en la lista de favoritas, pero no deberá aparecer en nuevas sugerencias ni menús mientras permanezca excluida (ver RN19).

**Diferencia entre exclusiones y restricciones alimentarias:** las restricciones alimentarias pertenecen al perfil del usuario e incluyen alergias, ingredientes y categorías a evitar. Estas se evalúan mediante las reglas de compatibilidad alimentaria.

Las exclusiones son preferencias explícitas sobre recetas individuales. Una receta puede ser compatible con el perfil del usuario y estar exclida igualmente. La exclusión no modifica las restricciones alimentarias del perfil.

### 4.6 Calificaciones

**RN9 — Rango de calificación:** `[MVP — pendiente]` la puntuación asignada a una receta deberá ser un número entero comprendido entre 1 y 5.

**RN10 — Calificación vigente:** `[MVP — pendiente]` cada usuario podrá mantener una única calificación vigente por receta.

**RN11 — Promedio:** `[MVP — pendiente]` la calificación promedio de una receta se calculará utilizando las calificaciones vigentes de los usuarios.

### 4.7 Reportes y moderación

**RN12 — Estados del reporte:** `[MVP — pendiente]` todo nuevo reporte deberá registrarse inicialmente con estado PENDIENTE. Los estados posibles son PENDIENTE, CERRADO y ACEPTADO.

**RN13 — Reporte pendiente:** `[MVP — pendiente]` mientras un reporte permanezca pendiente, la receta reportada dejará de aparecer en nuevas sugerencias y menús del usuario que realizó el reporte (ver RN19).

**RN14 — Reporte cerrado:** `[MVP — pendiente]` si el Administrador/Moderador cierra el reporte sin tomar acciones sobre la receta, esta podrá volver a aparecer para el usuario siempre que continúe respetando las restricciones de su perfil.

**RN15 — Reporte aceptado:** `[MVP — pendiente]` si el Administrador/Moderador acepta el reporte, la receta deberá quedar desactivada preventivamente y no podrá utilizarse en nuevas sugerencias o menús de ningún usuario.

### 4.8 Permisos del Administrador/Moderador

**RN16 — Alcance del Moderador:** `[MVP — pendiente]` el Administrador/Moderador puede consultar y resolver reportes y desactivar preventivamente recetas.

**RN17 — Restricciones del Moderador:** `[MVP — pendiente]` el Administrador/Moderador no puede crear ni modificar recetas, ingredientes, alternativas de ingredientes ni información nutricional, ni reactivar recetas desactivadas.

**RN18 — Revisión posterior:** `[MVP — pendiente]` en el MVP la desactivación preventiva de una receta es definitiva: no existe reactivación. La revisión, corrección o validación del contenido de una receta desactivada corresponderá al actor Profesional en una etapa posterior al MVP.

### 4.9 Visibilidad de recetas

**RN19 — Visibilidad de recetas:** `[DEMO — parcial; MVP para reportes]` la aparición de una receta para un usuario se rige por la siguiente tabla.

| **Situación de la receta** | **Sugerencias y menús nuevos** | **Catálogo y consulta manual** | **Etapa** |
| --- | --- | --- | --- |
| Excluida por el usuario | Se excluye de propuestas automáticas; requiere revisión explícita si se incorpora manualmente | Puede consultarse | DEMO |
| Ingrediente restringido sin alternativa válida | No se ofrece como opción válida para un menú | La API puede indicar INCOMPATIBLE mediante consulta explícita | DEMO |
| Ingrediente restringido con alternativa válida | Puede presentarse como ADAPTABLE y requiere confirmación para guardarse | El detalle de compatibilidad informa las alternativas; la presentación en listados requiere ajustes | DEMO, con mejora pendiente |
| Reporte pendiente del usuario | No se sugerirá | Continúa consultable según regla proyectada | MVP |
| Desactivada preventivamente por moderación | No se ofrecerá | No aparecerá en nuevas consultas | MVP |

Los menús históricos guardados conservan la instantánea de las recetas y sustituciones del momento del guardado. **En la demo, ese historial no se revalida ni se marca automáticamente como no disponible**; esta lógica será necesaria al implementar la reutilización del MVP. Las reglas basadas en reportes y moderación tampoco se ejecutan en la demo.

### 4.10 Cuentas

**RN20 — Eliminación de cuenta:** `[MVP — opcional]` al eliminar su cuenta, se eliminan el perfil alimentario, los menús guardados, las recetas favoritas y excluidas y los datos personales del usuario. Las calificaciones y los reportes se conservan de forma anónima, sin asociarse a ningún dato personal, para no alterar los promedios ni el historial de moderación.

**RN21 — Cuentas de Administrador/Moderador:** `[MVP — pendiente]` las cuentas de Administrador/Moderador se crearán fuera de la aplicación (carga inicial o script de administración). El MVP no incluye registro ni gestión de cuentas de moderador.

### 4.11 Validaciones propias de la DEMO

**RN22 — Completitud del menú:** `[DEMO — implementado]` el menú de 1 a 7 días debe tener todas las posiciones seleccionadas confirmadas y al menos una comida por día; no se guardan propuestas incompletas.

**RN23 — Validación de sustituciones:** `[DEMO — implementado]` cada sustitución confirmada debe corresponder a una posición de ingrediente de la receta, pertenecer al conjunto de alternativas precargadas y respetar las restricciones actuales del usuario. Todos los ingredientes restringidos requieren una sustitución válida antes del guardado.

**RN24 — Historial y pertenencia:** `[DEMO — implementado]` solo el titular accede o elimina sus menús. Una vez guardado, el menú conserva una instantánea histórica independiente de modificaciones posteriores en el catálogo. No se reutiliza automáticamente ni se recalcula al consultarlo.

## 5. Requerimientos no funcionales

### 5.1 Seguridad

**RNF1 — Almacenamiento de contraseñas:** el sistema debe almacenar las contraseñas de los usuarios utilizando un mecanismo seguro de hash y no debe almacenarlas en texto plano.

**RNF2 — Autenticación:** el acceso a las funcionalidades que requieran autenticación debe realizarse mediante un mecanismo basado en tokens con tiempo de expiración.

**RNF3 — Autorización por roles (MVP proyectado):** el sistema debe impedir que un usuario acceda a funcionalidades reservadas al Administrador/Moderador y viceversa, de acuerdo con los permisos definidos para cada rol.

**RNF4 — Protección de datos:** un usuario autenticado solo debe poder acceder y modificar los datos asociados a su propia cuenta, perfil y menús, excepto aquellas operaciones expresamente habilitadas para el Administrador/Moderador.

### 5.2 Rendimiento

**RNF5 — Tiempo de respuesta (objetivo por verificar):** en un entorno local con el catálogo precargado, se propone que las operaciones habituales de consulta, generación y modificación respondan en menos de **3 segundos**. La demo no dispone de una medición formal que permita certificar este umbral. 

### 5.3 Integridad y confiabilidad

**RNF6 — Integridad de la información:** en la demo, el sistema debe mantener la consistencia de perfiles, menús, favoritas, exclusiones y sustituciones. En el MVP proyectado se extenderá esta obligación a calificaciones y reportes, y a la eliminación de cuenta si se implementa (RN20).

**RNF7 — Persistencia:** la información confirmada por el usuario debe mantenerse almacenada de forma persistente y estar disponible en posteriores accesos a su cuenta.

### 5.4 Mantenibilidad

**RNF8 — Organización del código:** la implementación debe mantener separadas las responsabilidades relacionadas con acceso a datos, lógica de negocio, autenticación y exposición de endpoints.

**RNF9 — Extensibilidad:** la arquitectura debe permitir incorporar nuevas funcionalidades, tipos de ingredientes, categorías, recetas y actores sin requerir modificaciones extensivas sobre los componentes existentes.

### 5.5 Documentación de la API

**RNF10 — Documentación:** los endpoints de la API deben estar documentados indicando, como mínimo, método HTTP, ruta, parámetros, datos de entrada, respuestas esperadas y posibles errores.

**RNF11 — Documentación interactiva:** la API desarrollada con FastAPI debe disponer de documentación interactiva para facilitar la consulta y prueba de sus endpoints.

### 5.6 Portabilidad y despliegue

**RNF12 — Contenedorización:** la aplicación debe poder ejecutarse dentro de un contenedor Docker con las dependencias necesarias para su funcionamiento.

**RNF13 — Configuración:** los valores sensibles o dependientes del entorno, como credenciales, claves y conexión a la base de datos, deben gestionarse mediante configuración externa y no quedar escritos directamente en el código fuente.

### 5.7 Calidad y pruebas

**RNF14 — Pruebas automatizadas:** el proyecto debe incluir pruebas automatizadas para verificar las principales reglas de negocio y funcionalidades de la API. La demo cuenta con pruebas de backend, mientras que la cobertura automatizada del frontend todavía es limitada.

**RNF15 — Ejecución automática de pruebas:** las pruebas deben poder ejecutarse automáticamente como parte del flujo de integración del proyecto.

## 6. Casos de uso

### 6.1 Perfil y cuenta

**CU1 — Registrarse:** `[DEMO — implementado]` el usuario crea una cuenta proporcionando los datos obligatorios requeridos por el sistema.

**CU2 — Iniciar sesión:** `[DEMO para Usuario; MVP para moderador]` el usuario se autentica con sus credenciales. Los permisos de moderación se incorporarán en el MVP.

**CU3 — Gestionar perfil alimentario:** `[DEMO — implementado]` el usuario crea o modifica su perfil indicando sus alergias alimentarias, los alimentos o ingredientes específicos y las categorías de alimentos que no consume o desea evitar, y su nivel culinario.

### 6.2 Generación y gestión de menús

**CU4 — Sugerir una comida:** `[DEMO — parcial]` el usuario selecciona un tipo de comida (desayuno, almuerzo, merienda o cena) y recibe hasta una cantidad máxima de opciones que respetan las restricciones de su perfil y su nivel culinario. Las recetas que requieren sustitución se indican como tales.

**CU5 — Generar menú diario:** `[DEMO — implementado]` el usuario selecciona las comidas que desea incluir en un día y el sistema genera un menú utilizando recetas disponibles según su perfil. Si alguna receta queda pendiente de sustitución, el sistema solicita al usuario seleccionar la alternativa antes de poder guardar el menú.

**CU6 — Generar menú para varios días:** `[DEMO — implementado]` el usuario selecciona un período de entre 2 y 7 días y las comidas que desea incluir en cada día. El sistema genera el menú evitando repetir recetas mientras existan otras opciones disponibles y solicita la selección de alternativas para las recetas pendientes de sustitución.

**CU7 — Reemplazar una receta del menú:** `[DEMO — parcial]` el usuario reemplaza una receta puntual de un menú diario o de varios días sin modificar el resto del menú. Si la receta de reemplazo requiere sustitución, el sistema solicita la selección de la alternativa.

**CU8 — Guardar menú:** `[DEMO — implementado]` el usuario guarda un menú generado y este queda asociado a su cuenta. Solo pueden guardarse menús sin recetas pendientes de sustitución.

**CU9 — Consultar menús guardados:** `[DEMO — implementado]` el usuario consulta el historial y el detalle de los menús que guardó previamente.

**CU10 — Reutilizar un menú guardado:** `[MVP — pendiente]` el usuario utiliza un menú anterior como base para crear uno nuevo. El sistema vuelve a verificar las recetas y sustituciones de acuerdo con las restricciones actuales del perfil y el estado actual de las recetas, sin modificar el menú histórico original. Las recetas que ya no sean válidas se marcan como no disponibles y el usuario debe reemplazarlas antes de guardar el nuevo menú.

### 6.3 Recetas

**CU11 — Consultar recetas:** `[DEMO — parcial]` el usuario explora el catálogo y consulta el detalle y la compatibilidad de las recetas. La consulta de compatibilidad identifica las adaptables; queda pendiente uniformar su presencia en todos los listados personalizados.

**CU12 — Ver detalle de receta:** `[DEMO — implementado]` el usuario consulta los ingredientes, cantidades, pasos de preparación, tiempo de preparación, nivel de dificultad, tipos de comida, información nutricional precargada (dato informativo del catálogo) y alternativas de ingredientes disponibles.

### 6.4 Alternativas de ingredientes

**CU13 — Seleccionar una alternativa de ingrediente:** `[DEMO — parcial]` el usuario consulta las alternativas definidas y confirma una alternativa válida para una comida del menú. En el detalle de una receta puede guardar o quitar su preferencia para ingredientes restringidos. La selección voluntaria general está permitida en la API de guardado, pero requiere completar su experiencia de interfaz.

### 6.5 Interacción con recetas

**CU14 — Gestionar favoritas y exclusiones:** `[DEMO — implementado]` el usuario puede marcar una receta como favorita, quitarla de favoritas, excluirla o eliminarla de sus exclusiones. Si una receta se encuentra simultáneamente como favorita y excluida, la exclusión tiene prioridad para las sugerencias y menús.

**CU15 — Calificar una receta:** `[MVP — pendiente]` el usuario califica una receta mediante una puntuación entera de 1 a 5 estrellas o modifica una calificación realizada anteriormente. El sistema mantiene una única calificación vigente del usuario para cada receta.

### 6.6 Reportes

**CU16 — Reportar una receta:** `[MVP — pendiente]` el usuario reporta una receta seleccionando un motivo y pudiendo agregar un comentario opcional. El reporte queda registrado inicialmente como pendiente y, mientras permanezca en ese estado, la receta deja de aparecer en nuevas sugerencias y menús del usuario que realizó el reporte.

### 6.7 Moderación

*Actor: Administrador/Moderador*

**CU17 — Consultar reportes:** `[MVP — pendiente]` el Administrador/Moderador consulta los reportes (por defecto, los pendientes), pudiendo filtrarlos por estado, y accede al detalle del reporte, la receta involucrada, el motivo y el comentario proporcionado por el usuario.

**CU18 — Resolver un reporte:** `[MVP — pendiente]` el Administrador/Moderador analiza un reporte y puede cerrarlo cuando no requiera acciones adicionales o aceptarlo cuando la receta requiera revisión. Si lo cierra, la receta podrá volver a aparecer para el usuario que realizó el reporte siempre que respete las restricciones de su perfil. Si lo acepta, la receta será desactivada preventivamente y dejará de aparecer en nuevas sugerencias y menús para todos los usuarios.

### 6.8 Exportación

**CU19 — Exportar menú a PDF:** `[MVP — opcional]` el usuario exporta un menú generado o guardado a un archivo PDF que contiene las comidas y recetas que lo componen.

*Prioridad: deseable / sujeta al alcance del MVP.*

### 6.9 Casos de uso secundarios

**CU20 — Recuperar contraseña:** `[MVP — opcional]` el usuario solicita el restablecimiento de su contraseña cuando no puede acceder a su cuenta.

**CU21 — Eliminar cuenta:** `[MVP — opcional]` el usuario autenticado solicita eliminar su cuenta y los datos personales asociados, según lo dispuesto en RN20.

*Prioridad de CU20 y CU21: secundaria / sujeta al alcance del MVP.*

### 6.10 Operaciones adicionales incluidas en la DEMO

**CU22 — Eliminar menú guardado:** `[DEMO — implementado]` el usuario elige un menú de su historial, confirma la eliminación y el sistema lo elimina si le pertenece.

**CU23 — Gestionar sustitución persistente de una receta:** `[DEMO — implementado]` el usuario consulta el detalle de una receta, selecciona una alternativa válida para un ingrediente restringido y la guarda o elimina de sus preferencias sin modificar la receta original.

## 7. Trazabilidad de la demo y criterios de aceptación

Esta tabla no reemplaza los requerimientos: vincula los flujos observables de la **demo que se presentará** con la implementación actual.

| Flujo demostrable | Requisitos | API principal | Criterio de aceptación |
| --- | --- | --- | --- |
| Registrar cuenta e iniciar sesión | RQ1; RF1–RF2; CU1–CU2 | `POST /cuentas`, `POST /auth/token` | El usuario obtiene una sesión válida y puede consultar su cuenta. |
| Crear y actualizar perfil | RQ2; RF7–RF10; CU3 | `POST /perfil`, `GET /perfil`, `PUT /perfil` | El perfil conserva alergias, ingredientes/categorías evitadas y nivel culinario. |
| Consultar recetas y compatibilidad | RQ3; RF11–RF14, RF29–RF31; CU11–CU12 | `GET /recetas`, `GET /recetas/{id}`, `GET /recetas/{id}/compatibilidad` | Puede verse el detalle y el estado de compatibilidad, con alternativas si existen. |
| Generar propuesta | RQ4; RF16–RF21; CU5–CU6 | `POST /menus/generar` | Se genera un menú de 1–7 días que usa tipos de comida solicitados; la propuesta no se guarda sola. |
| Reemplazar receta antes del guardado | RQ5; RF22–RF24; CU7 | Interfaz + validación de `POST /menus` | Puede cambiarse una comida; el backend verifica la elección al guardar. |
| Confirmar sustitución dentro del menú | RQ6; RF34–RF36, RF56, RF62; CU13 | `GET /recetas/{id}/compatibilidad`, `POST /menus` | La receta restringida exige confirmación válida y el guardado conserva la alternativa elegida. |
| Guardar, listar, consultar y eliminar un menú | RQ5; RF25–RF27, RF58–RF59, RF61; CU8–CU9, CU22 | `POST /menus`, `GET /menus`, `GET /menus/{id}`, `DELETE /menus/{id}` | El menú aparece en el historial después de recargar, conserva la instantánea y puede eliminarse por su titular. |
| Gestionar una preferencia de sustitución | RQ6; RF60; CU23 | `GET/PUT/DELETE /recetas/{id}/sustituciones/...` | La preferencia de sustitución válida puede guardarse, consultarse y quitarse. |
| Marcar favorita o excluir receta | RQ7; RF37–RF41; CU14 | `GET /recetas/favoritas`, `GET /recetas/excluidas` y endpoints de modificación | Las preferencias de recetas se conservan por usuario. |

