
 ## Diagrama de capas Onion: Registro, Venta y Desembolso

* Dominio:
  *  Entidades principales: Cliente, Empresa, Factura, Planilla.
  *  Reglas de negocio: validación de datos, cálculo de tasas de descuento, control de desembolsos.

* Aplicación:
  * Casos de uso organizados por módulo:
    * Registro (cuenta y empresa).
    * Venta (planillas, pricing, negociación).
    * Desembolso (transferencia y notificación).

* Infraestructura:
  * Persistencia con ORM y DB.
  * Integraciones externas: SUNAT (SOAP), APIs REST, bancos, notificaciones.

* Presentación:
  * Interfaces web y móviles.
  * Bandeja de solicitudes para gestión del cliente.


## 📊 Diagrama de Capas
```mermaid
flowchart TB
    %% Núcleo de Dominio
    subgraph Dominio["🧅 Núcleo de Dominio"]
        Entidades["Entidades: Cliente, Empresa, Factura, Planilla"]
        Reglas["Reglas de Negocio: Validación, Pricing, Desembolso"]
    end

    %% Capa de Aplicación
    subgraph Aplicacion["⚙️ Capa de Aplicación"]
        CasosRegistro["Casos de Uso: Registro de Cuenta/Empresa"]
        CasosVenta["Casos de Uso: Venta/Factoring (Planillas, Pricing)"]
        CasosDesembolso["Casos de Uso: Desembolso de Facturas"]
    end

    %% Infraestructura
    subgraph Infraestructura["🗄️ Infraestructura"]
        DB["Persistencia: SQLAlchemy / MySQL / PostgreSQL"]
        SOAP["Servicios SOAP: Validación SUNAT, Tributaria"]
        REST["APIs REST/GraphQL: Exposición de servicios"]
        Notificacion["Servicio de Notificación: Email, SMS"]
        Banco["Integración Bancaria: Transferencias, Cuentas"]
    end

    %% Presentación
    subgraph Presentacion["💻 Presentación"]
        Web["Web App Flask/FastAPI"]
        UI["Frontend React/Angular"]
        Bandeja["Módulo Bandeja de Solicitudes"]
    end

    %% Relaciones
    Entidades --> Reglas
    Reglas --> CasosRegistro
    Reglas --> CasosVenta
    Reglas --> CasosDesembolso

    CasosRegistro --> DB
    CasosRegistro --> SOAP

    CasosVenta --> DB
    CasosVenta --> SOAP
    CasosVenta --> REST
    CasosVenta --> Notificacion

    CasosDesembolso --> DB
    CasosDesembolso --> Banco
    CasosDesembolso --> Notificacion

    Web --> REST
    UI --> REST
    Bandeja --> REST
```

## Requerimientos funcionales del módulo “Registro”
RF01 y RF02: El usuario registra primero sus datos personales y luego los de la empresa.

RF03: Puede ingresar a la plataforma, pero con acceso limitado hasta que se validen los datos.

RF04: Se realiza la validación con servicios externos (RUC, cuentas bancarias, representante legal).

RF05: Una vez confirmada la validación, se notifica al usuario y se habilita el acceso completo.

## 📊 Diagrama de Secuencia “Registro”
```mermaid
sequenceDiagram
    participant U as Usuario
    participant W as Web Plataforma Factoring
    participant DB as Base de Datos
    participant V as Servicio de Validación Externa
    participant N as Servicio de Notificación

    %% RF01: Registro de Datos de la Cuenta
    U->>W: RF01. Registrar datos de cuenta (DNI, Nombre, Dirección, Teléfono, Correo, Fecha Nacimiento, Contraseña)
    W->>DB: Guardar datos básicos de la cuenta
    DB-->>W: Confirmación de registro de cuenta

    %% RF02: Registro de Datos de la Empresa
    U->>W: RF02. Registrar datos de la empresa (RUC, Razón Social, Representante Legal, Cuentas Bancarias, Documentos)
    W->>DB: Guardar datos complementarios de la empresa
    DB-->>W: Confirmación de registro de empresa

    %% RF03: Ingreso a la Plataforma
    U->>W: RF03. Ingresar con DNI + Contraseña
    W->>DB: Validar credenciales
    DB-->>W: Credenciales válidas
    W-->>U: Acceso limitado (solo consulta, sin operaciones de factoring)

    %% RF04: Validación de Datos de la Empresa
    W->>V: Validar RUC, DNI, Representante Legal, Cuentas Bancarias, Moneda
    V-->>W: Resultado de validación
    W->>DB: Actualizar estado de validación

    %% RF05: Notificación de Registro Completo
    W->>N: Notificar al usuario registro completo
    N-->>U: Confirmación: Plataforma habilitada al 100%
    W-->>U: Acceso total a operaciones de factoring
```


## Requerimientos funcionales del módulo “Venta”
RF01–RF03: El cliente gestiona sus planillas (consulta, registro, desestimación).

RF04–RF05: La plataforma valida las facturas con SUNAT y ejecuta reglas de pricing.

RF06: Se notifica al cliente la tasa y simulación de desembolso.

RF07: El cliente puede negociar la tasa con un ejecutivo y finalmente aprobarla para el desembolso.

## 📊 Diagrama de Secuencia “Venta”
```mermaid
sequenceDiagram
    participant C as Cliente
    participant W as Plataforma Factoring
    participant DB as Base de Datos
    participant S as SUNAT (Validación)
    participant P as Motor de Pricing
    participant E as Ejecutivo de Pricing
    participant N as Servicio de Notificación

    %% RF01: Bandeja de Solicitudes
    C->>W: RF01. Consultar bandeja de solicitudes
    W->>DB: Obtener planillas registradas
    DB-->>W: Lista de planillas
    W-->>C: Mostrar bandeja con opciones (detalle, descargar PDF)

    %% RF02: Registro de Planilla
    C->>W: RF02. Registrar planilla con facturas (1-90)
    W->>DB: Guardar planilla y facturas
    DB-->>W: Confirmación de registro

    %% RF03: Desestimar Planilla
    C->>W: RF03. Desestimar planilla con motivos
    W->>DB: Actualizar estado de planilla a "Desestimada"
    DB-->>W: Confirmación de desestimación
    W-->>C: Notificación de planilla desestimada

    %% RF04: Validar Vigencia de Facturas
    W->>S: Validar vigencia de facturas con SUNAT
    S-->>W: Resultado de validación
    W->>DB: Actualizar estado de facturas

    %% RF05: Ejecutar Reglas de Pricing
    W->>P: Ejecutar reglas de pricing (Girador, Deudores, Montos, Posición)
    P-->>W: Calcular tasa de descuento (Total o Parcial)
    W->>DB: Guardar tasa calculada

    %% RF06: Notificar Tasa y Simulación
    W->>N: Notificar tasa y simulación de desembolso
    N-->>C: Correo con detalle de tasa y desembolso
    W-->>C: Bandeja actualizada con información de tasa

    %% RF07: Negociar Tasa
    C->>W: RF07. Solicitar negociación de tasa
    W->>E: Iniciar proceso de negociación
    E-->>W: Propuesta ajustada de tasa
    W-->>C: Mostrar nueva tasa negociada

    %% RF07: Aprobación de Tasa y Desembolso
    C->>W: Aceptar condiciones (Tasa + Importe)
    W->>DB: Actualizar estado de solicitud a "Aprobada"
    DB-->>W: Confirmación
    W-->>C: Solicitud lista para desembolso

```

## Requerimientos funcionales del módulo “Desembolso”
RF01: La plataforma marca la factura como negociada en SUNAT para evitar duplicidad de operaciones.

RF02: Se realiza la transferencia del monto descontado a la cuenta del cliente.

RF03: Se notifica al cliente que el desembolso fue realizado y la solicitud cambia de estado.

## 📊 Diagrama de Secuencia “Desembolso”
```mermaid
sequenceDiagram
    participant C as Cliente
    participant W as Plataforma Factoring
    participant DB as Base de Datos
    participant S as SUNAT
    participant B as Banco/Entidad Financiera
    participant N as Servicio de Notificación

    %% RF01: Anotación en Cuenta de las Facturas
    W->>S: RF01. Marcar factura como Negociada/Vendida
    S-->>W: Confirmación de anotación en SUNAT
    W->>DB: Actualizar estado de factura (Negociada/Vendida)

    %% RF02: Transferencia del Monto Descontado
    W->>B: RF02. Solicitar transferencia del monto descontado
    B-->>W: Confirmación de transferencia realizada
    W->>DB: Actualizar estado de solicitud a "Desembolsado"

    %% RF03: Notificar al Cliente
    W->>N: RF03. Notificar monto desembolsado
    N-->>C: Correo con detalle del desembolso
    W-->>C: Solicitud cambia a estado "Desembolsado"

```
  
  