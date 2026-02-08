# Limitaciones Conocidas - Template Matching

## Limitaciones del sistema de detección

### 1. Velocidad de actualización de recursos
**Problema:** Cuando los recursos cambian muy rápido (ej: cheat "aegis"), el sistema puede no detectar correctamente algunos valores intermedios.

**Causa:** El reconocimiento opera a ~5 FPS y el template matching toma tiempo. Si el número cambia durante la captura, puede haber frames mal leídos.

**Impacto:** Bajo. En partidas normales los recursos no cambian tan rápido.

**Mitigación:** El sistema usa fallback al último valor válido.

---

### 2. Límite de dígitos: hasta 999,999
**Problema:** El juego muestra un "carrusel" (animación de scroll) cuando los recursos superan ~1,000,000. El sistema NO puede leer valores durante esta animación.

**Causa:** El carrusel hace que los dígitos se muevan, lo que rompe el template matching estático.

**Impacto:** Muy bajo. En partidas normales es casi imposible llegar a 1M de recursos.

**Recomendación:** Considerar valores > 999,999 como "overflow" y mostrar "999k+" en la UI.

---

### 3. Resolución fija: 1920x1080
**Problema:** La calibración actual solo funciona para resolución 1920x1080.

**Solución futura:** Crear calibraciones para otras resoluciones o implementar auto-calibración.

---

### 4. Template matching vs OCR
**Decisión:** Se eligió template matching sobre OCR porque:
- OCR (Tesseract) fallaba con los colores del juego (cyan, amarillo)
- Template matching es más robusto para fuentes conocidas
- Menor latencia

---

## Registro de cambios

| Fecha | Cambio |
|-------|--------|
| 2026-02-07 | Documentación inicial de limitaciones |
