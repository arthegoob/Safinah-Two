import { createClient } from "@supabase/supabase-js";

export async function POST(req: Request) {
  if (req.headers.get("x-api-key") !== process.env.UPLOAD_KEY) {
    return Response.json({ error: "unauthorized" }, { status: 401 });
  }

  const form = await req.formData();
  const file = form.get("image") as File | null;
  if (!file) {
    return Response.json({ error: "tidak ada gambar" }, { status: 400 });
  }

  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!
  );

  const nama = `${Date.now()}.jpg`;
  const { error } = await supabase.storage
    .from("captures")
    .upload(nama, file, { contentType: "image/jpeg" });

  if (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
  return Response.json({ ok: true, file: nama });
}