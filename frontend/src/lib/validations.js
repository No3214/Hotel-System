import { z } from 'zod';

export const reservationSchema = z.object({
  guest_id: z.string().min(1, 'Misafir secimi zorunlu'),
  room_type: z.string().min(1, 'Oda tipi secimi zorunlu'),
  check_in: z.string().min(1, 'Giris tarihi zorunlu').regex(/^\d{4}-\d{2}-\d{2}$/, 'Gecersiz tarih formati'),
  check_out: z.string().min(1, 'Cikis tarihi zorunlu').regex(/^\d{4}-\d{2}-\d{2}$/, 'Gecersiz tarih formati'),
  guests_count: z.coerce.number().int().min(1, 'En az 1 kisi olmali').max(20, 'En fazla 20 kisi'),
  total_price: z.union([z.literal(''), z.coerce.number().min(0, 'Fiyat negatif olamaz')]).optional(),
  notes: z.string().max(500, 'Notlar en fazla 500 karakter olabilir').optional(),
}).refine(data => {
  if (data.check_in && data.check_out) {
    return data.check_out > data.check_in;
  }
  return true;
}, { message: 'Cikis tarihi giris tarihinden sonra olmali', path: ['check_out'] });

export const guestSchema = z.object({
  name: z.string().min(2, 'Ad en az 2 karakter olmali').max(100, 'Ad en fazla 100 karakter'),
  email: z.union([z.literal(''), z.string().email('Gecersiz e-posta adresi')]).optional(),
  phone: z.string().max(20, 'Telefon en fazla 20 karakter').optional(),
  nationality: z.string().max(50, 'Uyruk en fazla 50 karakter').optional(),
  notes: z.string().max(500, 'Notlar en fazla 500 karakter').optional(),
});

export const financialSchema = z.object({
  type: z.enum(['income', 'expense'], { message: 'Gelir veya gider secin' }),
  amount: z.coerce.number().positive('Tutar pozitif olmali'),
  category: z.string().min(1, 'Kategori zorunlu'),
  description: z.string().max(500).optional(),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Gecersiz tarih').optional(),
});

/**
 * Validate form data against a Zod schema.
 * Returns { success: true, data } or { success: false, errors: { field: message } }
 */
export function validateForm(schema, data) {
  const result = schema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data, errors: {} };
  }
  const errors = {};
  for (const issue of result.error.issues) {
    const field = issue.path.join('.');
    if (!errors[field]) {
      errors[field] = issue.message;
    }
  }
  return { success: false, data: null, errors };
}
