# NutriPlanner — Documentación de requisitos

Especificación de requisitos del MVP

> NutriPlanner es una plataforma de planificación alimentaria que filtra recetas precargadas según las restricciones alimentarias y el nivel culinario del usuario, y permite organizar menús personalizados.

---

## Índice

1. [Idea de negocio](#1-idea-de-negocio)
2. [Requerimientos de alto nivel](#2-requerimientos-de-alto-nivel)
3. [Requerimientos funcionales](#3-requerimientos-funcionales)
4. [Reglas de negocio](#4-reglas-de-negocio)
5. [Requerimientos no funcionales](#5-requerimientos-no-funcionales)
6. [Casos de uso](#6-casos-de-uso)

---

## 1. Idea de negocio

NutriPlanner es una plataforma de planificación alimentaria que permite generar menús personalizados orientados a una alimentación saludable a partir de las alergias, los alimentos o ingredientes específicos y las categorías de alimentos que el usuario no consume o desea evitar, y su nivel culinario.

El sistema parte de una base de recetas precargada y previamente definida para el MVP. Cada receta contiene sus ingredientes, cantidades, uno o más tipos de comida, nivel de dificultad, información nutricional precargada y, cuando corresponda, alternativas previamente establecidas para determinados ingredientes.

Para el MVP, el sistema no calcula automáticamente si una receta es saludable ni calcula valores nutricionales. Las recetas disponibles forman parte de un catálogo precargado y previamente seleccionado para el proyecto, y la información nutricional que se muestra es un dato informativo precargado en dicho catálogo. La personalización realizada por NutriPlanner consiste en filtrar y organizar las recetas según las restricciones alimentarias y el nivel culinario del usuario.

A partir del perfil del usuario, NutriPlanner filtra las recetas disponibles y genera propuestas de menú evitando los ingredientes restringidos por las alergias declaradas o por los alimentos que el usuario haya indicado que no desea consumir. Una receta con ingredientes restringidos solo se ofrece cuando existe una alternativa previamente definida, que el usuario debe seleccionar para poder incorporarla a su menú.

**Problema que resuelve:** una persona puede querer alimentarse de manera más organizada o evitar determinados alimentos, pero eso no necesariamente le resuelve qué cocinar, qué recetas respetan sus restricciones alimentarias, qué alternativas puede utilizar para determinados ingredientes ni cómo organizar varios días de comidas sin repetir siempre lo mismo. NutriPlanner busca simplificar esa planificación ofreciendo recetas y menús personalizados a partir de la información proporcionada por el usuario.

### 1.1 Actores del MVP

**Usuario**

Es el actor principal de la plataforma. Puede:

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
- reutilizar menús guardados;
- gestionar recetas favoritas y excluidas;
- calificar recetas mediante una puntuación de 1 a 5 estrellas;
- reportar recetas cuando detecte algún inconveniente.

**Administrador/Moderador**

Es un actor interno autorizado encargado de gestionar los reportes realizados por los usuarios. Puede:

- consultar los reportes, filtrándolos por estado (pendiente, cerrado o aceptado);
- consultar el detalle de un reporte;
- cerrar un reporte cuando determine que no requiere acciones adicionales;
- aceptar un reporte cuando considere que requiere revisión;
- desactivar preventivamente una receta asociada a un reporte aceptado.

El Administrador/Moderador no crea ni modifica recetas, ingredientes, sustituciones ni información nutricional, y no reactiva recetas desactivadas. Tampoco realiza validaciones profesionales sobre el contenido alimentario.

### 1.2 Alcance del MVP

El MVP de NutriPlanner contempla:

- registro y autenticación de usuarios;
- autenticación y autorización del Administrador/Moderador;
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
- guardado, consulta y reutilización de menús;
- gestión de recetas favoritas y excluidas;
- consulta y selección de alternativas precargadas para determinados ingredientes;
- conservación de las sustituciones elegidas dentro del menú correspondiente;
- calificación de recetas de 1 a 5 estrellas;
- consulta de la valoración promedio de una receta;
- reporte de recetas;
- gestión de reportes por parte del Administrador/Moderador, incluida su consulta por estado.

### 1.3 Funcionalidades deseables o secundarias

Las siguientes funcionalidades podrán incorporarse al MVP si el alcance y los tiempos de implementación lo permiten:

- **Exportación de menús a PDF** (prioridad: deseable).
- **Recuperación de contraseña** (prioridad: secundaria).
- **Eliminación de cuenta y de los datos personales asociados** (prioridad: secundaria).

### 1.4 Fuera de alcance (visión futura)

Incorporación de profesionales, lista de compras, comercios, publicidad, geolocalización, marketplace, obras sociales/prepagas, diagnóstico o prescripción médica, cálculo de calorías/macronutrientes y reactivación de recetas desactivadas.

### 1.5 Plan de monetización

El modelo de monetización corresponde a una evolución comercial posterior al MVP. Por lo tanto, el MVP académico no contempla la implementación de pagos, suscripciones ni publicidad.

En una futura etapa comercial, NutriPlanner adoptaría un modelo freemium. El plan gratuito permitiría utilizar las funcionalidades principales de la plataforma y podría financiarse parcialmente mediante publicidad no invasiva. El plan Premium se plantea como una suscripción mensual o anual que ofrecería funcionalidades avanzadas y una experiencia sin publicidad.

| **Plan** | **Características previstas**                                                                                           | **Modalidad**               |
| -------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| Gratuito | Consulta de recetas, generación básica de menús y funcionalidades principales de planificación                          | Publicidad no invasiva      |
| Premium  | Mayor personalización, historial y reutilización ampliada de menús, herramientas avanzadas y experiencia sin publicidad | Suscripción mensual o anual |

El objetivo del plan gratuito sería permitir que el usuario conozca y utilice el servicio sin realizar un pago inicial. El plan Premium constituiría la principal fuente de ingresos prevista, mientras que la publicidad contribuiría al sostenimiento de los costos asociados a los usuarios gratuitos.


```text
                     [ MVP ]

  Implementación y validación de funciones principales

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

**RQ1 — Gestión de cuenta:** el usuario podrá registrarse y autenticarse para acceder a las funcionalidades asociadas a su cuenta. Los usuarios internos autorizados podrán autenticarse para acceder a las funciones de moderación.

**RQ2 — Gestión del perfil alimentario:** el usuario podrá configurar y modificar sus alergias alimentarias, los alimentos o ingredientes específicos y las categorías de alimentos que no consume o desea evitar, y su nivel culinario.

**RQ3 — Consulta personalizada de recetas:** el usuario podrá consultar recetas adecuadas a su perfil, acceder a su detalle y conocer las alternativas disponibles para determinados ingredientes.

**RQ4 — Generación de menús:** el usuario podrá recibir sugerencias y generar menús personalizados para períodos de hasta siete días, utilizando desayuno, almuerzo, merienda y cena como tipos de comida.

**RQ5 — Gestión de menús:** el usuario podrá reemplazar recetas, guardar menús, consultar su historial y reutilizar menús anteriores.

**RQ6 — Personalización de recetas:** el usuario podrá seleccionar alternativas previamente definidas para determinados ingredientes cuando una receta las contemple.

**RQ7 — Gestión de favoritas, exclusiones y calificaciones:** el usuario podrá marcar recetas como favoritas, excluirlas y calificarlas mediante una puntuación de 1 a 5 estrellas.

**RQ8 — Reporte y moderación de recetas:** el usuario podrá reportar recetas en las que detecte algún inconveniente, y el Administrador/Moderador podrá consultar, cerrar o aceptar esos reportes y desactivar preventivamente las recetas asociadas a reportes aceptados.

**RQ9 — Exportación:** el usuario podrá exportar sus menús a PDF.

*Prioridad: deseable.*

**RQ10 — Gestión avanzada de la cuenta:** el usuario podrá restablecer su contraseña y eliminar su cuenta y los datos personales asociados.

*Prioridad: secundaria / sujeta al alcance del MVP.*

## 3. Requerimientos funcionales

### 3.1 Autenticación y cuenta

**RF1.** El sistema debe permitir al usuario registrarse proporcionando los datos obligatorios de la cuenta, incluyendo correo electrónico, nombre de usuario y contraseña.

**RF2.** El sistema debe permitir al usuario autenticarse mediante sus credenciales registradas para acceder a las funcionalidades asociadas a su cuenta.

**RF3.** El sistema debe permitir al Administrador/Moderador autenticarse mediante una cuenta interna autorizada (ver RN21).

**RF4.** El sistema debe restringir las funcionalidades disponibles de acuerdo con el rol autenticado, diferenciando las funciones del Usuario de las funciones del Administrador/Moderador.

**RF5.** El sistema debe permitir al usuario solicitar el restablecimiento de su contraseña cuando no pueda acceder a su cuenta.

**RF6.** El sistema debe permitir al usuario autenticado eliminar su cuenta y los datos personales asociados, según lo dispuesto en RN20.

*Prioridad de RF5 y RF6: secundaria / sujeta al alcance del MVP.*

### 3.2 Perfil alimentario

**RF7.** El sistema debe permitir al usuario indicar sus alergias alimentarias a partir de un catálogo predefinido.

**RF8.** El sistema debe permitir al usuario seleccionar alimentos o ingredientes específicos y categorías de alimentos que no consume o desea evitar, a partir de los catálogos definidos por el sistema.

**RF9.** El sistema debe permitir al usuario indicar su nivel culinario.

**RF10.** El sistema debe almacenar el perfil alimentario del usuario y permitir su modificación.

### 3.3 Filtrado y personalización de recetas

**RF11.** El sistema debe considerar las restricciones del perfil alimentario (alergias, alimentos o ingredientes específicos y categorías de alimentos a evitar) al determinar las recetas que puede ofrecerle al usuario.

**RF12.** El sistema debe considerar restringidos los alimentos o ingredientes asociados a una alergia declarada por el usuario, sin aplicar niveles intermedios de restricción o priorización. Una receta que contenga un ingrediente restringido por alergia solo podrá ofrecerse si existe una alternativa válida previamente definida para dicho ingrediente, en cuyo caso deberá indicarse que requiere sustitución.

**RF13.** Cuando una receta contenga uno o más ingredientes restringidos por el perfil del usuario, el sistema solo podrá ofrecerla si existe una alternativa válida previamente definida para cada uno de ellos. Si para alguno no existe una alternativa válida, la receta no deberá ser sugerida, incluida en menús ni listada.

**RF14.** El sistema debe utilizar el nivel culinario del usuario para personalizar las recetas que le sugiere automáticamente, según la correspondencia definida en RN3.

### 3.4 Generación de menús

**RF15.** El sistema debe permitir al usuario seleccionar un tipo de comida entre desayuno, almuerzo, merienda y cena y mostrarle hasta una cantidad máxima de recetas disponibles definida por el sistema.

**RF16.** El sistema debe permitir al usuario generar un menú diario seleccionando las comidas que desea incluir.

**RF17.** El sistema debe permitir al usuario generar un menú para un período de entre 2 y 7 días, seleccionando las comidas que desea incluir en cada día.

**RF18.** El sistema debe permitir visualizar el menú generado, mostrando los días seleccionados, las comidas incluidas y la receta asignada a cada una.

**RF19.** El sistema debe evitar repetir una misma receta dentro del período generado mientras existan otras recetas disponibles suficientes.

**RF20.** El sistema debe informar al usuario cuando no existan recetas disponibles para una comida solicitada que respeten las restricciones definidas en su perfil.

**RF21.** El sistema debe excluir de las sugerencias y menús las recetas que el usuario haya marcado como excluidas (ver RN19).

### 3.5 Reemplazo de recetas en un menú

**RF22.** El sistema debe permitir al usuario reemplazar una receta puntual de un menú generado.

**RF23.** El sistema debe ofrecer como reemplazo otras recetas disponibles de acuerdo con el perfil del usuario y diferentes de las ya incluidas en el menú, siempre que existan opciones disponibles.

**RF24.** El sistema debe mantener sin cambios el resto del menú cuando se reemplace una receta.

### 3.6 Guardado de menús

**RF25.** El sistema debe permitir al usuario guardar un menú generado, asociándolo a su cuenta para poder consultarlo posteriormente, siempre que no contenga recetas pendientes de sustitución (RF56).

### 3.7 Consulta y reutilización de menús guardados

**RF26.** El sistema debe mostrar al usuario el historial de sus menús guardados.

**RF27.** El sistema debe permitir al usuario consultar el detalle de un menú guardado.

**RF28.** El sistema debe permitir al usuario reutilizar un menú guardado como base para un nuevo menú, conservando inicialmente las recetas que lo componen, sujetas a la revalidación definida en RN7 y RF57, y permitiendo realizar reemplazos, sin modificar el menú guardado original.

**RF57.** Al reutilizar un menú guardado, el sistema debe revalidar cada receta y sustitución según el perfil actual del usuario y el estado actual de las recetas. Toda receta que ya no sea válida debe marcarse como no disponible, y el usuario deberá reemplazarla antes de guardar el nuevo menú. Toda receta cuya sustitución ya no sea válida debe quedar pendiente de sustitución (RF56).

### 3.8 Consulta de recetas

**RF29.** El sistema debe permitir al usuario consultar recetas que respeten las restricciones de su perfil alimentario, sin limitar el listado según su nivel culinario. Las recetas que contengan ingredientes restringidos con alternativa válida se muestran indicando que requieren sustitución.

**RF30.** El sistema debe mostrar el detalle de una receta, incluyendo:

- ingredientes;
- cantidades;
- pasos de preparación;
- tiempo de preparación;
- nivel de dificultad;
- uno o más tipos de comida asociados;
- información nutricional precargada (dato informativo del catálogo; el sistema no la calcula);
- alternativas disponibles para determinados ingredientes, cuando existan.

**RF31.** El sistema debe indicar en el detalle de una receta cuáles de sus ingredientes admiten alternativas previamente definidas.

### 3.9 Alternativas de ingredientes

**RF32.** El sistema debe permitir al usuario consultar las alternativas previamente definidas para un ingrediente de una receta cuando estas existan.

**RF33.** El sistema debe impedir que se ofrezca como alternativa un ingrediente que entre en conflicto con las restricciones del perfil alimentario del usuario.

**RF34.** El sistema debe permitir al usuario seleccionar una alternativa válida para sustituir un ingrediente dentro de una receta.

**RF35.** La selección de una alternativa no debe modificar la receta original almacenada en el catálogo.

**RF36.** Cuando una receta forme parte de un menú, el sistema debe conservar la alternativa seleccionada por el usuario asociada a esa receta dentro de dicho menú.

**RF56.** Cuando un menú generado, o el reemplazo de una receta, incluya una receta con ingredientes restringidos que cuenten con alternativa válida, el sistema debe marcar la receta como pendiente de sustitución y solicitar al usuario que seleccione una alternativa para cada ingrediente restringido. El sistema no debe permitir guardar un menú que contenga recetas pendientes de sustitución.

### 3.10 Favoritas y exclusiones

**RF37.** El sistema debe permitir al usuario marcar una receta como favorita desde las sugerencias, los menús y el listado de recetas.

**RF38.** El sistema debe permitir al usuario consultar sus recetas favoritas.

**RF39.** El sistema debe permitir al usuario quitar una receta de sus favoritas.

**RF40.** El sistema debe permitir al usuario excluir una receta para que deje de aparecer en sus sugerencias, menús y listados personalizados (ver RN19).

**RF41.** El sistema debe permitir al usuario quitar una receta de sus exclusiones, habilitando nuevamente su aparición cuando resulte adecuada a su perfil.

### 3.11 Calificación de recetas

**RF42.** El sistema debe permitir al usuario calificar una receta mediante una puntuación de 1 a 5 estrellas.

**RF43.** El sistema debe permitir al usuario modificar la calificación que haya otorgado previamente a una receta.

**RF44.** El sistema debe mantener una única calificación vigente por usuario y receta.

**RF45.** El sistema debe calcular y mostrar la calificación promedio de una receta a partir de las valoraciones realizadas por los usuarios.

**Resumen de funciones sobre recetas**

| **Función** | **Para qué sirve**                               |
| ----------- | ------------------------------------------------ |
| Favorita    | Guardar una receta que quiero volver a consultar |
| Excluir     | No quiero que esa receta vuelva a aparecer       |
| Calificar   | Expresar cuánto me gustó mediante 1–5 estrellas  |

### 3.12 Reporte y moderación de recetas

**RF46.** El sistema debe permitir al usuario reportar una receta seleccionando un motivo de un catálogo predefinido y pudiendo agregar un comentario opcional.

**RF47.** El sistema debe registrar el reporte asociándolo al usuario, la receta, el motivo, el comentario opcional y su estado.

**RF48.** El sistema debe impedir que un usuario tenga más de un reporte pendiente sobre la misma receta.

**RF49.** Mientras exista un reporte pendiente realizado por un usuario sobre una receta, el sistema debe excluir dicha receta de las nuevas sugerencias y menús de ese usuario (ver RN19).

**RF50.** El sistema debe permitir al Administrador/Moderador consultar los reportes, pudiendo filtrarlos por estado (pendiente, cerrado o aceptado). Por defecto se muestran los reportes pendientes.

**RF51.** El sistema debe permitir al Administrador/Moderador consultar el detalle de un reporte.

**RF52.** El sistema debe permitir al Administrador/Moderador cerrar un reporte cuando no requiera acciones adicionales.

**RF53.** El sistema debe permitir al Administrador/Moderador aceptar un reporte y desactivar preventivamente la receta asociada.

**RF54.** El sistema debe impedir que una receta desactivada aparezca en nuevas sugerencias, menús o listados para cualquier usuario (ver RN19).

### 3.13 Exportación

**RF55.** El sistema debe permitir al usuario exportar a PDF un menú generado o guardado, incluyendo las comidas y recetas que lo componen.

*Prioridad: deseable.*

## 4. Reglas de negocio

### 4.1 Restricciones del perfil alimentario

En este documento se denominan **restricciones del perfil alimentario** al conjunto formado por las alergias declaradas, los alimentos o ingredientes específicos y las categorías de alimentos que el usuario no consume o desea evitar.

**RN1 — Alergias:** los alimentos o ingredientes asociados a una alergia declarada por el usuario deben considerarse restringidos. La restricción es obligatoria: el sistema no debe moderar ni priorizar su aparición. Una receta que contenga un ingrediente restringido por alergia solo podrá ofrecerse cuando exista una alternativa válida previamente definida, quedando pendiente de sustitución hasta que el usuario seleccione dicha alternativa. 

**RN2 — Alimentos, ingredientes y categorías a evitar:** cuando el usuario indique que no consume o desea evitar un alimento o ingrediente específico, ese ingrediente se considerará restringido. Cuando indique una categoría de alimentos, se considerarán restringidos todos los ingredientes pertenecientes a dicha categoría.

### 4.2 Nivel culinario

**RN3 — Nivel culinario:** para las sugerencias automáticas de recetas se aplicará la siguiente correspondencia:

| **Nivel del usuario** | **Niveles de recetas sugeridos**    |
| --------------------- | ----------------------------------- |
| Principiante          | Principiante                        |
| Intermedio            | Principiante e Intermedio           |
| Avanzado              | Principiante, Intermedio y Avanzado |

El nivel culinario no impedirá que el usuario consulte manualmente recetas de otros niveles desde el catálogo.

### 4.3 Alternativas de ingredientes

**RN4 — Sustitución obligatoria:** cuando una receta contenga un ingrediente restringido por el perfil del usuario y exista una alternativa válida, la receta se considera pendiente de sustitución. El usuario deberá seleccionar una alternativa antes de poder guardar el menú que la contiene. Si la receta contiene varios ingredientes restringidos, debe existir y seleccionarse una alternativa válida para cada uno; si para alguno no existe, la receta no se ofrece.

Ejemplo:

Usuario evita: azúcar

Receta:        azúcar (restringido)

Alternativas:  miel ✓   otro endulzante ✓

→ la receta queda pendiente de sustitución

→ el usuario debe elegir una alternativa para poder guardar el menú

**RN5 — Sustitución opcional:** cuando el ingrediente original no esté restringido, el usuario podrá conservarlo o seleccionar voluntariamente alguna de las alternativas disponibles.

**RN6 — Persistencia de la sustitución:** la alternativa elegida debe almacenarse junto con la receta utilizada en el menú y no debe modificar la receta original del catálogo.

### 4.4 Reutilización de menús

**RN7 — Revalidación del menú:** al reutilizar un menú guardado, el sistema deberá volver a verificar sus recetas y sustituciones según las restricciones actuales del perfil del usuario y el estado actual de las recetas. Las recetas que ya no sean válidas se marcarán como no disponibles y deberán reemplazarse antes de guardar el nuevo menú; las sustituciones que ya no sean válidas dejarán la receta pendiente de sustitución. El menú histórico original permanecerá sin modificaciones.

Ejemplo:

Menú antiguo:  Pizza con queso

Después el usuario agrega:  Evitar → Lácteos

Al reutilizar el menú:

→ la receta se verifica de nuevo

→ si no existe alternativa válida, se marca como no disponible y debe reemplazarse

Menú histórico:

→ permanece intacto

### 4.5 Favoritas y exclusiones

**RN8 — Prioridad de la exclusión:** si una misma receta se encuentra simultáneamente marcada como favorita y excluida, la exclusión tendrá prioridad. La receta podrá mantenerse en la lista de favoritas, pero no deberá aparecer en nuevas sugerencias ni menús mientras permanezca excluida (ver RN19).

### 4.6 Calificaciones

**RN9 — Rango de calificación:** la puntuación asignada a una receta deberá ser un número entero comprendido entre 1 y 5.

**RN10 — Calificación vigente:** cada usuario podrá mantener una única calificación vigente por receta.

**RN11 — Promedio:** la calificación promedio de una receta se calculará utilizando las calificaciones vigentes de los usuarios.

### 4.7 Reportes y moderación

**RN12 — Estados del reporte:** todo nuevo reporte deberá registrarse inicialmente con estado PENDIENTE. Los estados posibles son PENDIENTE, CERRADO y ACEPTADO.

**RN13 — Reporte pendiente:** mientras un reporte permanezca pendiente, la receta reportada dejará de aparecer en nuevas sugerencias y menús del usuario que realizó el reporte (ver RN19).

**RN14 — Reporte cerrado:** si el Administrador/Moderador cierra el reporte sin tomar acciones sobre la receta, esta podrá volver a aparecer para el usuario siempre que continúe respetando las restricciones de su perfil.

**RN15 — Reporte aceptado:** si el Administrador/Moderador acepta el reporte, la receta deberá quedar desactivada preventivamente y no podrá utilizarse en nuevas sugerencias o menús de ningún usuario.

### 4.8 Permisos del Administrador/Moderador

**RN16 — Alcance del Moderador:** el Administrador/Moderador puede consultar y resolver reportes y desactivar preventivamente recetas.

**RN17 — Restricciones del Moderador:** el Administrador/Moderador no puede crear ni modificar recetas, ingredientes, alternativas de ingredientes ni información nutricional, ni reactivar recetas desactivadas.

**RN18 — Revisión posterior:** en el MVP la desactivación preventiva de una receta es definitiva: no existe reactivación. La revisión, corrección o validación del contenido de una receta desactivada corresponderá al actor Profesional en una etapa posterior al MVP.

### 4.9 Visibilidad de recetas

**RN19 — Visibilidad de recetas:** la aparición de una receta para un usuario se rige por la siguiente tabla.

| **Situación de la receta**                     | **Sugerencias y menús nuevos**        | **Listado de recetas**                     | **Alcance**                 |
| ---------------------------------------------- | ------------------------------------- | ------------------------------------------ | --------------------------- |
| Excluida por el usuario                        | No aparece                            | No aparece                                 | Solo ese usuario            |
| Reporte pendiente del usuario                  | No aparece                            | Sigue visible                              | Solo ese usuario            |
| Desactivada por moderación                     | No aparece                            | No aparece                                 | Todos los usuarios          |
| Ingrediente restringido sin alternativa válida | No aparece                            | No aparece                                 | Según el perfil del usuario |
| Ingrediente restringido con alternativa válida | Aparece como pendiente de sustitución | Aparece indicando que requiere sustitución | Según el perfil del usuario |

Los menús guardados no se modifican: si una receta incluida en un menú guardado fue luego excluida, reportada o desactivada, el menú histórico permanece intacto y la receta se muestra marcada como no disponible.

### 4.10 Cuentas

**RN20 — Eliminación de cuenta:** al eliminar su cuenta, se eliminan el perfil alimentario, los menús guardados, las recetas favoritas y excluidas y los datos personales del usuario. Las calificaciones y los reportes se conservan de forma anónima, sin asociarse a ningún dato personal, para no alterar los promedios ni el historial de moderación.

**RN21 — Cuentas de Administrador/Moderador:** las cuentas de Administrador/Moderador se crean fuera de la aplicación (carga inicial o script de administración). El MVP no incluye registro ni gestión de cuentas de moderador.

## 5. Requerimientos no funcionales

### 5.1 Seguridad

**RNF1 — Almacenamiento de contraseñas:** el sistema debe almacenar las contraseñas de los usuarios utilizando un mecanismo seguro de hash y no debe almacenarlas en texto plano.

**RNF2 — Autenticación:** el acceso a las funcionalidades que requieran autenticación debe realizarse mediante un mecanismo basado en tokens con tiempo de expiración.

**RNF3 — Autorización por roles:** el sistema debe impedir que un usuario acceda a funcionalidades reservadas al Administrador/Moderador y viceversa, de acuerdo con los permisos definidos para cada rol.

**RNF4 — Protección de datos:** un usuario autenticado solo debe poder acceder y modificar los datos asociados a su propia cuenta, perfil y menús, excepto aquellas operaciones expresamente habilitadas para el Administrador/Moderador.

### 5.2 Rendimiento

**RNF5 — Tiempo de respuesta:** En un entorno local con el catálogo precargado, las operaciones habituales de consulta, generación y modificación deben responder en menos de **3 segundos**. 

### 5.3 Integridad y confiabilidad

**RNF6 — Integridad de la información:** el sistema debe mantener la consistencia de los datos ante operaciones de creación, modificación o eliminación de perfiles, menús, calificaciones, exclusiones y reportes, incluida la eliminación de cuenta (RN20).

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

**RNF14 — Pruebas automatizadas:** el proyecto debe incluir pruebas automatizadas para verificar las principales reglas de negocio y funcionalidades de la API.

**RNF15 — Ejecución automática de pruebas:** las pruebas deben poder ejecutarse automáticamente como parte del flujo de integración del proyecto.

## 6. Casos de uso

### 6.1 Perfil y cuenta

**CU1 — Registrarse:** el usuario crea una cuenta proporcionando los datos obligatorios requeridos por el sistema.

**CU2 — Iniciar sesión:** el Usuario o Administrador/Moderador se autentica mediante sus credenciales. El sistema habilita las funcionalidades correspondientes según su rol.

**CU3 — Gestionar perfil alimentario:** el usuario crea o modifica su perfil indicando sus alergias alimentarias, los alimentos o ingredientes específicos y las categorías de alimentos que no consume o desea evitar, y su nivel culinario.

### 6.2 Generación y gestión de menús

**CU4 — Sugerir una comida:** el usuario selecciona un tipo de comida (desayuno, almuerzo, merienda o cena) y recibe hasta una cantidad máxima de opciones que respetan las restricciones de su perfil y su nivel culinario. Las recetas que requieren sustitución se indican como tales.

**CU5 — Generar menú diario:** el usuario selecciona las comidas que desea incluir en un día y el sistema genera un menú utilizando recetas disponibles según su perfil. Si alguna receta queda pendiente de sustitución, el sistema solicita al usuario seleccionar la alternativa antes de poder guardar el menú.

**CU6 — Generar menú para varios días:** el usuario selecciona un período de entre 2 y 7 días y las comidas que desea incluir en cada día. El sistema genera el menú evitando repetir recetas mientras existan otras opciones disponibles y solicita la selección de alternativas para las recetas pendientes de sustitución.

**CU7 — Reemplazar una receta del menú:** el usuario reemplaza una receta puntual de un menú diario o de varios días sin modificar el resto del menú. Si la receta de reemplazo requiere sustitución, el sistema solicita la selección de la alternativa.

**CU8 — Guardar menú:** el usuario guarda un menú generado y este queda asociado a su cuenta. Solo pueden guardarse menús sin recetas pendientes de sustitución.

**CU9 — Consultar menús guardados:** el usuario consulta el historial y el detalle de los menús que guardó previamente.

**CU10 — Reutilizar un menú guardado:** el usuario utiliza un menú anterior como base para crear uno nuevo. El sistema vuelve a verificar las recetas y sustituciones de acuerdo con las restricciones actuales del perfil y el estado actual de las recetas, sin modificar el menú histórico original. Las recetas que ya no sean válidas se marcan como no disponibles y el usuario debe reemplazarlas antes de guardar el nuevo menú.

### 6.3 Recetas

**CU11 — Consultar recetas:** el usuario explora las recetas que respetan las restricciones de su perfil alimentario, incluidas las que requieren sustitución, indicadas como tales. El nivel culinario no impide la consulta manual de recetas de mayor dificultad.

**CU12 — Ver detalle de receta:** el usuario consulta los ingredientes, cantidades, pasos de preparación, tiempo de preparación, nivel de dificultad, tipos de comida, información nutricional precargada (dato informativo del catálogo) y alternativas de ingredientes disponibles.

### 6.4 Alternativas de ingredientes

**CU13 — Seleccionar una alternativa de ingrediente:** el usuario consulta las alternativas previamente definidas para un ingrediente y selecciona una alternativa válida. La selección es opcional cuando el ingrediente original está permitido y obligatoria cuando dicho ingrediente está restringido y la receta requiere una sustitución para poder incorporarse a un menú guardado.

### 6.5 Interacción con recetas

**CU14 — Gestionar favoritas y exclusiones:** el usuario puede marcar una receta como favorita, quitarla de favoritas, excluirla o eliminarla de sus exclusiones. Si una receta se encuentra simultáneamente como favorita y excluida, la exclusión tiene prioridad para las sugerencias y menús.

**CU15 — Calificar una receta:** el usuario califica una receta mediante una puntuación entera de 1 a 5 estrellas o modifica una calificación realizada anteriormente. El sistema mantiene una única calificación vigente del usuario para cada receta.

### 6.6 Reportes

**CU16 — Reportar una receta:** el usuario reporta una receta seleccionando un motivo y pudiendo agregar un comentario opcional. El reporte queda registrado inicialmente como pendiente y, mientras permanezca en ese estado, la receta deja de aparecer en nuevas sugerencias y menús del usuario que realizó el reporte.

### 6.7 Moderación

*Actor: Administrador/Moderador*

**CU17 — Consultar reportes:** el Administrador/Moderador consulta los reportes (por defecto, los pendientes), pudiendo filtrarlos por estado, y accede al detalle del reporte, la receta involucrada, el motivo y el comentario proporcionado por el usuario.

**CU18 — Resolver un reporte:** el Administrador/Moderador analiza un reporte y puede cerrarlo cuando no requiera acciones adicionales o aceptarlo cuando la receta requiera revisión. Si lo cierra, la receta podrá volver a aparecer para el usuario que realizó el reporte siempre que respete las restricciones de su perfil. Si lo acepta, la receta será desactivada preventivamente y dejará de aparecer en nuevas sugerencias y menús para todos los usuarios.

### 6.8 Exportación

**CU19 — Exportar menú a PDF:** el usuario exporta un menú generado o guardado a un archivo PDF que contiene las comidas y recetas que lo componen.

*Prioridad: deseable / sujeta al alcance del MVP.*

### 6.9 Casos de uso secundarios

**CU20 — Recuperar contraseña:** el usuario solicita el restablecimiento de su contraseña cuando no puede acceder a su cuenta.

**CU21 — Eliminar cuenta:** el usuario autenticado solicita eliminar su cuenta y los datos personales asociados, según lo dispuesto en RN20.

*Prioridad de CU20 y CU21: secundaria / sujeta al alcance del MVP.*
