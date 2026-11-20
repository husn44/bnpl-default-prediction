# LLM Scoring Prompts & Test Results

## 1. Customer Financial Stress Scoring

### Prompt
> Read this customer message. Rate the customer's financial stress from 1 (very calm) to 5 (very stressed). Reply with only the number.
> Message: [paste message here]

### Test Results (5 Examples)
1. **Message:** "Hi, boleh tak I delay my instalment this month? Company baru retrench staff semalam, tengah cari kerja baru sekarang."
   * **Expected Level:** High Stress
   * **LLM Output:** `5`

2. **Message:** "Tolong sangat, gaji masuk lambat bulan ni, can you waive the late fee for 5 days?"
   * **Expected Level:** High Stress
   * **LLM Output:** `5`

3. **Message:** "Hi, just checking kalau saya bayar lambat sehari dua, berapa ringgit late fee kena caj?"
   * **Expected Level:** Medium Stress
   * **LLM Output:** `3`

4. **Message:** "Boleh tak tukar due date saya dari 25hb ke 1hb? Gaji saya masuk setiap hujung bulan."
   * **Expected Level:** Medium Stress
   * **LLM Output:** `2`

5. **Message:** "Hi, saya nak tukar alamat penghantaran untuk order baru saya, baru pindah rumah minggu lepas."
   * **Expected Level:** Low Stress
   * **LLM Output:** `1`

---

## 2. Product Description Impulse Appeal Scoring

### Prompt
> Read this product description. Rate how strongly it encourages impulse buying from 1 (very plain/factual) to 5 (high urgency/impulse). Reply with only the number.
> Description: [paste description here]

### Test Results (5 Examples)
1. **Description:** "FLASH SALE TONIGHT ONLY! Viral Korean hydrating lip tint 50% OFF—grab yours before all shades sell out!"
   * **Expected Level:** High Impulse
   * **LLM Output:** `5`

2. **Description:** "LAST 5 UNITS LEFT! Oversized aesthetic streetwear hoodie—instant RM30 voucher expires in 2 hours!"
   * **Expected Level:** High Impulse
   * **LLM Output:** `5`

3. **Description:** "10kg fragrant Thai white rice, vacuum-sealed pack for daily family cooking and long-term pantry storage."
   * **Expected Level:** Normal / Factual
   * **LLM Output:** `1`

4. **Description:** "Ergonomic mesh office chair with adjustable seat height, lumbar support, and 360-degree swivel wheels."
   * **Expected Level:** Normal / Factual
   * **LLM Output:** `1`

5. **Description:** "Minimalist 3-tier wooden bookshelf made from engineered wood, dimensions 80cm x 30cm x 100cm."
   * **Expected Level:** Normal / Factual
   * **LLM Output:** `1`
