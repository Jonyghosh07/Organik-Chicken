-- disable asiapay payment provider
UPDATE payment_provider
   SET amrpy_store_id = NULL,
       amrpy_signature_key = NULL,
