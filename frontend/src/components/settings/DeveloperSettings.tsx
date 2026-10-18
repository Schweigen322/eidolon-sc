"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { SettingsSection } from "@/components/app/SettingsSection";
import { Button } from "@/components/ui/button";
import { Field, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

type Item = { id: string; name: string };
type State = {
  characters: Item[]; gifts: Item[]; backups: string[]; affinity_on: boolean;
  affinities: { character_id: string; value: number; cooling: number }[];
  gift_balances: { draws: number; reset_cards: number }[];
  gift_backpacks: { gift_id: string; count: number }[];
};

async function request<T>(path: string, body?: object, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api/developer${path}`, {
    cache: "no-store", signal,
    ...(body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {}),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(response.status === 404 ? "此账号未开启开发者工具，请先由部署者配置授权用户 ID。" : error.detail || "请求失败，请重试");
  }
  return response.json();
}

function Choice({ label, value, items, onChange }: { label: string; value: string; items: Item[]; onChange: (value: string) => void }) {
  return <Field><FieldLabel>{label}</FieldLabel><Select value={value} onValueChange={(v) => { if (v) onChange(v); }}>
    <SelectTrigger aria-label={label} className="w-full"><SelectValue>{items.find((i) => i.id === value)?.name ?? "请选择"}</SelectValue></SelectTrigger>
    <SelectContent>{items.map((i) => <SelectItem key={i.id} value={i.id}>{i.name}</SelectItem>)}</SelectContent>
  </Select></Field>;
}

/** 原生设置表单：同一套页面同时用于电脑右栏与手机二级设置。 */
export function DeveloperSettings({ mode }: { mode: "sheet" | "play" }) {
  const [data, setData] = useState<State | null>(null);
  const [character, setCharacter] = useState("");
  const [gift, setGift] = useState("");
  const [backup, setBackup] = useState("");
  const [score, setScore] = useState(50);
  const [draws, setDraws] = useState(0);
  const [cards, setCards] = useState(0);
  const [count, setCount] = useState(0);
  const [sheet, setSheet] = useState("");
  const [original, setOriginal] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const dirty = original !== null && sheet !== original;
  const dirtyRef = useRef(false);
  dirtyRef.current = dirty;

  const reload = useCallback(async () => {
    const next = await request<State>("/state");
    setData(next);
    setCharacter((value) => value || next.characters[0]?.id || "");
    setGift((value) => value || next.gifts[0]?.id || "");
    setBackup((value) => next.backups.includes(value) ? value : next.backups[0] || "");
    setDraws(next.gift_balances[0]?.draws ?? 0);
    setCards(next.gift_balances[0]?.reset_cards ?? 0);
  }, []);

  useEffect(() => { reload().catch((e: Error) => setError(e.message)); }, [reload]);
  useEffect(() => { setScore(data?.affinities.find((a) => a.character_id === character)?.value ?? 50); }, [data, character]);
  useEffect(() => { setCount(data?.gift_backpacks.find((g) => g.gift_id === gift)?.count ?? 0); }, [data, gift]);
  useEffect(() => {
    if (mode !== "sheet" || !character) return;
    const controller = new AbortController();
    setOriginal(null); setSheet(""); setError("");
    request<{ text: string }>(`/sheet?character=${encodeURIComponent(character)}`, undefined, controller.signal)
      .then((result) => { setOriginal(result.text); setSheet(result.text); })
      .catch((e: Error) => { if (e.name !== "AbortError") setError(e.message); });
    return () => controller.abort();
  }, [character, mode]);
  useEffect(() => {
    const before = (event: BeforeUnloadEvent) => { if (dirtyRef.current) { event.preventDefault(); event.returnValue = ""; } };
    window.addEventListener("beforeunload", before);
    return () => window.removeEventListener("beforeunload", before);
  }, []);

  async function change(body: object) {
    if (busy) return;
    setBusy(true); setError(""); setNotice("");
    try {
      const result = await request<{ message: string; backup: string }>("/change", body);
      await reload();
      setNotice(`已保存，刷新聊天页面查看。修改前备份：${result.backup}`);
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }
  async function saveSheet() {
    if (busy || original === null) return;
    setBusy(true); setError(""); setNotice("");
    try {
      const result = await request<{ message: string }>("/sheet", { character, text: sheet, original });
      setOriginal(sheet); setNotice(result.message);
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  }

  return <>
    {error && <p role="alert" className="py-4 text-body text-destructive">{error}</p>}
    {notice && <p role="status" className="py-4 text-body text-muted-foreground">{notice}</p>}
    {!data ? <SettingsSection description={error ? "确认配置后可重新读取。" : "正在读取…"}><Button variant="outline" onClick={() => reload().then(() => setError("")).catch((e: Error) => setError(e.message))}>重新读取</Button></SettingsSection> :
      <fieldset disabled={busy} className="min-w-0">
        <SettingsSection description={mode === "sheet" ? "调整角色性格、称呼和关系设定。保存前自动备份，修改影响本部署中的所有用户。" : "调整当前登录账号的玩法数据。请先结束通话、等待回复完成，再保存修改。"}>
          <Choice label="角色" value={character} items={data.characters} onChange={(value) => {
            if (dirty && !window.confirm("人设尚未保存，放弃修改并切换角色？")) return;
            setCharacter(value); setNotice("");
          }} />
        </SettingsSection>
        {mode === "sheet" ? <>
          <SettingsSection title="角色人设" description="具体写明说话方式、关系和行为习惯，避免与现有段落矛盾。">
            <Field><FieldLabel htmlFor="developer-sheet">人设内容</FieldLabel><Textarea id="developer-sheet" value={sheet} disabled={original === null} maxLength={80000} rows={18} onChange={(event) => setSheet(event.target.value)} /></Field>
            <div className="flex flex-wrap items-center gap-3"><Button disabled={!dirty || !sheet.trim()} onClick={saveSheet}>{busy ? "正在保存…" : "保存"}</Button><Button variant="ghost" disabled={!dirty} onClick={() => { if (original !== null && window.confirm("撤销未保存的人设修改？")) setSheet(original); }}>撤销修改</Button><span className="text-meta text-muted-foreground">{original === null ? "正在读取" : dirty ? "有修改未保存" : "已保存"}</span></div>
          </SettingsSection>
          <SettingsSection description="保存后新回复使用新人设，无需重启。进行中的通话请挂断后重拨；旧对话风格可能延续，建议新建对话测试。" />
        </> : <>
          {!data.affinity_on && <SettingsSection description="判断模型尚未启用，好感度和礼物暂不参与聊天。这里保存的数据会保留，配置好判断模型后再使用。" />}
          <SettingsSection title="好感度与冷却" description="数值范围 0–100。保存正数会解除冷却并重置当日对话增长计数；保存 0 会进入冷却。低于 50 时仍会自然恢复。">
            <Field><FieldLabel htmlFor="developer-score">当前好感度</FieldLabel><Input id="developer-score" type="number" min={0} max={100} step={1} value={score} onChange={(e) => setScore(Number(e.target.value))} /></Field>
            <div className="flex flex-wrap gap-2">{[10, 50, 80, 100].map((value) => <Button key={value} variant="outline" onClick={() => setScore(value)}>{value === 50 ? "50 · 默认" : value}</Button>)}</div>
            <p className="text-meta text-muted-foreground">数据库冷却状态：{data.affinities.find((a) => a.character_id === character)?.cooling ? "冷却中" : "未冷却"}</p>
            <Button className="self-start" onClick={() => change({ action: "affinity", character, value: score })}>保存好感度</Button>
          </SettingsSection>
          <SettingsSection title="抽奖与重置卡" description="填写的是最终持有数量。抽奖次数沿用原玩法上限 7 次。">
            <Field><FieldLabel htmlFor="developer-draws">抽奖次数</FieldLabel><Input id="developer-draws" type="number" min={0} max={7} value={draws} onChange={(e) => setDraws(Number(e.target.value))} /></Field>
            <Field><FieldLabel htmlFor="developer-cards">重置卡数量</FieldLabel><Input id="developer-cards" type="number" min={0} max={9999} value={cards} onChange={(e) => setCards(Number(e.target.value))} /></Field>
            <div className="flex flex-wrap gap-2"><Button variant="outline" onClick={() => setDraws(7)}>补满 7 次</Button><Button onClick={() => change({ action: "balances", draws, cards })}>保存次数与重置卡</Button></div>
          </SettingsSection>
          <SettingsSection title="礼物背包">
            <Choice label="礼物" value={gift} items={data.gifts} onChange={setGift} />
            <Field><FieldLabel htmlFor="developer-count">持有数量</FieldLabel><Input id="developer-count" type="number" min={0} max={9999} value={count} onChange={(e) => setCount(Number(e.target.value))} /></Field>
            <div className="flex flex-wrap gap-2"><Button variant="outline" onClick={() => setCount(99)}>设为 99</Button><Button onClick={() => change({ action: "gift", gift, count })}>保存礼物数量</Button></div>
          </SettingsSection>
          <SettingsSection title="恢复备份" description="每次修改前自动备份。恢复仅影响当前账号的好感度和背包，不覆盖聊天或其他账号。">
            {data.backups.length ? <><Choice label="修改前的备份" value={backup} items={data.backups.map((name) => ({ id: name, name }))} onChange={setBackup} /><Button variant="outline" className="self-start" onClick={() => { if (window.confirm("恢复当前账号的好感度、礼物和抽奖余额？当前数据也会先备份。")) change({ action: "restore", backup }); }}>恢复此备份</Button></> : <p className="text-body text-muted-foreground">还没有修改记录</p>}
          </SettingsSection>
        </>}
      </fieldset>}
  </>;
}
