(* ============================================================ *)
(* GESTIÓN DE PETICIONES (TP1 y TP2) - Mantenemos lógica original *)
(* ============================================================ *)

TP1( In := TareZeroReq, PT := TareZeroTime, Q => TareZeroStart );

(* REUTILIZAMOS LoadScaleReq: Antes era "Calibrar con Pesas", 
   ahora es "Guardar Pendientes del Excel" *)
TP2( In := LoadScaleReq, PT := LoadScaleTime, Q => LoadScaleStart );


(* ============================================================ *)
(* 1. CALIBRACIÓN DE CERO (EN PISO) - Mantenemos lógica original *)
(* ============================================================ *)

(* Interlock: Solo tarar si está LANDED y SIN CANDADOS *)
TareZeroInterlockOk := NOT SpreaderTwistlocksLocked AND SpreaderLanded;

IF TareZeroStart AND TareZeroInterlockOk THEN
   (* Guardamos el valor RAW actual como Cero *)
   LoadCellLeft1ZeroOffset := LoadCellLeft1.Value;
   LoadCellLeft2ZeroOffset := LoadCellLeft2.Value;
   LoadCellRight1ZeroOffset := LoadCellRight1.Value;
   LoadCellRight2ZeroOffset := LoadCellRight2.Value;
END_IF;


(* ============================================================ *)
(* 2. ACTUALIZACIÓN DE PENDIENTES (DESDE EXCEL/HMI)            *)
(* ============================================================ *)
(* Aquí eliminamos la dependencia de "TestLoadWeight" y el error de dividir por 4 *)

IF LoadScaleStart THEN
   (* Guardamos los valores ingresados en HMI (Del Excel) en memoria permanente *)
   Stored_Slope_L1 := r_Excel_Slope_L1;
   Stored_Slope_L2 := r_Excel_Slope_L2;
   Stored_Slope_R1 := r_Excel_Slope_R1;
   Stored_Slope_R2 := r_Excel_Slope_R2;
END_IF;

(* Reset manual de factor de desgaste (Solo al cambiar celda física) *)
IF x_Reset_Wear_Factor THEN
    r_Wear_Compensation := 1.0;
END_IF;


(* ============================================================ *)
(* 3. CÁLCULO DE PESO INDIVIDUAL (CORE DEL CAMBIO)             *)
(* ============================================================ *)
(* Fórmula: (Raw - Zero) * PendienteExcel * FactorDesgaste *)

(* Nota: Asignamos a variables temporales o directo a la salida según tu estructura *)

(* Left 1 *)
LoadCellLeft1Out.Value := (LoadCellLeft1.Value - LoadCellLeft1ZeroOffset) * Stored_Slope_L1 * r_Wear_Compensation;

(* Left 2 *)
LoadCellLeft2Out.Value := (LoadCellLeft2.Value - LoadCellLeft2ZeroOffset) * Stored_Slope_L2 * r_Wear_Compensation;

(* Right 1 *)
LoadCellRight1Out.Value := (LoadCellRight1.Value - LoadCellRight1ZeroOffset) * Stored_Slope_R1 * r_Wear_Compensation;

(* Right 2 *)
LoadCellRight2Out.Value := (LoadCellRight2.Value - LoadCellRight2ZeroOffset) * Stored_Slope_R2 * r_Wear_Compensation;


(* ============================================================ *)
(* 4. AUTO-LEARNING (INTELIGENCIA ARTIFICIAL SIMPLE)            *)
(* ============================================================ *)

(* Calculamos el Peso Bruto Total Actual *)
r_Current_Gross_Weight := LoadCellLeft1Out.Value + LoadCellLeft2Out.Value + LoadCellRight1Out.Value + LoadCellRight2Out.Value;

(* Definimos cuál DEBERÍA ser el peso (Spreader + Headblock) *)
r_Target_Tare_Weight := SpreaderWeight + HeadBlockWeight;

(* Condición: En el aire, Candados Abiertos, Grúa Quieta *)
(* Usamos SpreaderLanded = FALSE para saber que está en el aire *)
timer_AutoLearn(IN := (NOT SpreaderLanded AND NOT SpreaderTwistlocksLocked AND x_Hoist_Stopped AND x_Spreader_In_Air), PT := T#5S);

IF timer_AutoLearn.Q THEN
    
    (* Sanity Check: Solo aprender si la lectura es razonable (ej. +/- 20% del peso teórico) *)
    (* Evita aprender errores si hay un mecánico subido al spreader *)
    IF (r_Current_Gross_Weight > (r_Target_Tare_Weight * 0.8)) AND (r_Current_Gross_Weight < (r_Target_Tare_Weight * 1.2)) THEN
        
        (* Ratio: ¿Cuánto deberíamos pesar / Cuánto pesamos realmente? *)
        (* Si pesamos MENOS de lo debido (desgaste), el Ratio será > 1.0 *)
        r_Instant_Ratio := r_Target_Tare_Weight / r_Current_Gross_Weight;
        
        (* Filtro de Aprendizaje Lento (0.05% por ciclo) *)
        r_Wear_Compensation := (r_Wear_Compensation * 0.9995) + (r_Instant_Ratio * r_Wear_Compensation * 0.0005);
        
    END_IF;
END_IF;

(* ============================================================ *)
(* 5. COPIAR RESTO DE ESTRUCTURA (LEGACY)                       *)
(* ============================================================ *)
(* Mantenemos el paso de status bits originales *)

LoadCellLeft1Out.Status := LoadCellLeft1.Status;
LoadCellLeft2Out.Status := LoadCellLeft2.Status;
LoadCellRight1Out.Status := LoadCellRight1.Status;
LoadCellRight2Out.Status := LoadCellRight2.Status;
