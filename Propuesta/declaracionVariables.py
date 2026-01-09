(* VARIABLES EXISTENTES (NO BORRAR) *)
VAR_INPUT
    LoadCellLeft1, LoadCellLeft2 : LoadCellStruct; (* Estructura existente *)
    LoadCellRight1, LoadCellRight2 : LoadCellStruct;
    
    TareZeroReq : BOOL;      (* Botón Tara (Cero) *)
    LoadScaleReq : BOOL;     (* Lo usaremos para "Actualizar Pendientes HMI" *)
    
    SpreaderTwistlocksLocked : BOOL;
    SpreaderLanded : BOOL;
    
    TestLoadWeight : REAL;   (* YA NO SE USA para cálculo, pero déjala para no romper enlaces *)
    HeadBlockWeight : REAL;  (* Peso Headblock (Parte de la tara constante) *)
    SpreaderWeight : REAL;   (* Peso Spreader (Parte de la tara constante) *)
    
    (* ... resto de variables de tiempo TP1, TP2 ... *)
END_VAR

(* VARIABLES NUEVAS NECESARIAS (AGREGAR ESTAS) *)
VAR_INPUT
    (* Señales adicionales para seguridad del Auto-Learning *)
    x_Hoist_Stopped : BOOL;    (* Freno cerrado / Vel 0 *)
    x_Spreader_In_Air : BOOL;  (* Altura > 2m *)
    
    (* Entradas para los valores del Excel (Pendientes) *)
    r_Excel_Slope_L1 : REAL; 
    r_Excel_Slope_L2 : REAL; 
    r_Excel_Slope_R1 : REAL; 
    r_Excel_Slope_R2 : REAL;
    
    (* Comando para resetear desgaste (celda nueva) *)
    x_Reset_Wear_Factor : BOOL;
END_VAR

VAR_PERSISTENT
    (* Factor de Desgaste Dinámico (El cerebro de la solución) *)
    r_Wear_Compensation : REAL := 1.0; 
    
    (* Pendientes Base (Se guardan aquí desde el Excel) *)
    Stored_Slope_L1, Stored_Slope_L2 : REAL := 0.008;
    Stored_Slope_R1, Stored_Slope_R2 : REAL := 0.008;
END_VAR

VAR
    (* Temporizador para estabilidad en el aire *)
    timer_AutoLearn : TON;
    r_Current_Gross_Weight : REAL;
    r_Target_Tare_Weight : REAL;
    r_Instant_Ratio : REAL;
END_VAR
