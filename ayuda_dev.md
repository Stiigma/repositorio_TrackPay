# Modelo Base de Pagos

El modelo base de pagos se diseñó para contener los atributos esenciales que cualquier tipo de pago debe tener. Este modelo será **abstracto**, lo que significa que no se creará una tabla directamente, pero servirá como base para modelos específicos como `PagoUnico` y `PagoRecurrente`.

---

## Atributos del Modelo Base

### 1. `usuario`
- **Modelo usado:** Clave foránea (ForeignKey).
- **Función:** Relaciona cada pago con un usuario propietario.
- **Explicación:**
  - Permite identificar quién es el dueño del pago.
  - La relación es de uno-a-muchos: un usuario puede tener muchos pagos, pero cada pago pertenece a un único usuario.
  - La opción de eliminación en cascada (`on_delete=models.CASCADE`) asegura que, si el usuario es eliminado, también se eliminan sus pagos asociados.
- **Utilidad:**
  - Permite consultas eficientes, como obtener todos los pagos de un usuario o identificar al propietario de un pago específico.

---

### 2. `monto`
- **Modelo usado:** Campo decimal (DecimalField).
- **Función:** Representa el importe del pago.
- **Explicación:**
  - Almacena valores numéricos con precisión decimal, ideal para datos financieros.
  - El número máximo de dígitos (enteros y decimales) y los decimales permitidos se pueden definir según las necesidades del sistema.
- **Utilidad:**
  - Es crucial para cualquier cálculo financiero o generación de reportes.

---

### 3. `concepto`
- **Modelo usado:** Campo de texto corto (CharField).
- **Función:** Breve descripción del propósito del pago.
- **Explicación:**
  - Almacena una descripción breve como "Suscripción Netflix" o "Pago de renta".
  - Se establece un límite de caracteres para garantizar un almacenamiento eficiente y organizado.
- **Utilidad:**
  - Proporciona contexto sobre el pago al usuario o administrador.

---

### 4. `estado`
- **Modelo usado:** Campo de texto corto (CharField) con opciones predefinidas.
- **Función:** Indica el estado actual del pago.
- **Explicación:**
  - Almacena valores como `pendiente`, `completado` o `cancelado`.
  - Usar opciones predefinidas asegura que solo se permitan valores válidos, reduciendo errores.
- **Utilidad:**
  - Facilita filtrar pagos por su estado, lo que es útil para mostrar pagos pendientes o generar notificaciones.

---

### 5. `fecha_creacion`
- **Modelo usado:** Campo de fecha y hora (DateTimeField) con auto llenado al crear.
- **Función:** Almacena la fecha y hora en que se creó el pago.
- **Explicación:**
  - Este campo se llena automáticamente al crear el registro, proporcionando un historial claro de cuándo fue añadido el pago.
- **Utilidad:**
  - Es esencial para reportes históricos y análisis de datos.

---

### 6. `fecha_actualizacion`
- **Modelo usado:** Campo de fecha y hora (DateTimeField) con auto llenado al modificar.
- **Función:** Almacena la última vez que se actualizó el registro del pago.
- **Explicación:**
  - Este campo se actualiza automáticamente cada vez que el registro se modifica.
  - Es útil para auditar cambios, como cuándo se marcó un pago como `completado`.
- **Utilidad:**
  - Facilita el seguimiento de cambios en los pagos y asegura que la información siempre esté actualizada.

---

## Justificación de `fecha_creacion` y `fecha_actualizacion`
- **`fecha_creacion`:** Permite saber cuándo se registró un pago por primera vez.
- **`fecha_actualizacion`:** Registra la última modificación en el pago, lo cual es importante para auditorías y seguimiento de cambios.

---

## Conclusión
Este modelo base encapsula la información común necesaria para cualquier tipo de pago. Es flexible y extensible, lo que permite usarlo como base para modelos más específicos como pagos únicos y recurrentes, asegurando consistencia y escalabilidad en el sistema.
