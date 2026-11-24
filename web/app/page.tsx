import { createClient } from "@supabase/supabase-js";

export const dynamic = "force-dynamic"; // selalu ambil data terbaru

export default async function Page() {
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!
  );

  const { data } = await supabase.storage.from("captures").list("", {
    limit: 12,
    sortBy: { column: "created_at", order: "desc" },
  });

  return (
    <main style={{ padding: 24 }}>
      <h1>Monitoring</h1>
      {!data?.length && <p>Belum ada foto.</p>}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        {data?.map((f) => (
          <img
            key={f.name}
            width={320}
            alt={f.name}
            src={
              supabase.storage.from("captures").getPublicUrl(f.name).data
                .publicUrl
            }
          />
        ))}
      </div>
    </main>
  );
}