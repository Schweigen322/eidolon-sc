"use client";

import { useEffect, useId, useState, type FormEvent } from "react";
import { SettingsSection } from "@/components/app/SettingsSection";
import { FailureNotice } from "@/components/app/FailureNotice";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Field, FieldDescription, FieldGroup, FieldLabel, FieldLegend, FieldSet } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { copy } from "@/i18n";
import { getProactiveSettings, listCharacters, saveProactiveSettings, type Character, type ProactiveSettings as Preferences } from "@/lib/api";
import { toFailure, type Failure } from "@/lib/failure";

const t = copy.proactive;

export function ProactiveSettings() {
  const id = useId();
  const [draft, setDraft] = useState<Preferences | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [failure, setFailure] = useState<Failure | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let cancelled = false;
    Promise.all([getProactiveSettings(), listCharacters()]).then(([settings, all]) => {
      if (!cancelled) { setDraft(settings); setCharacters(all); }
    }, error => { if (!cancelled) setFailure(toFailure(error)); });
    return () => { cancelled = true; };
  }, [attempt]);

  function edit(change: Partial<Preferences>) {
    setSaved(false);
    setDraft(value => value && ({ ...value, ...change }));
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!draft || saving) return;
    setSaving(true); setFailure(null); setSaved(false);
    try { setDraft(await saveProactiveSettings(draft)); setSaved(true); }
    catch (error) { setFailure(toFailure(error)); }
    finally { setSaving(false); }
  }
  if (!draft) return <SettingsSection title={t.title}>
    {failure ? <><FailureNotice failure={failure} /><Button variant="outline" onClick={() => { setFailure(null); setAttempt(n => n + 1); }}>{t.retry}</Button></> : <p>{t.loading}</p>}
  </SettingsSection>;
  const noCharacter = draft.enabled && draft.characters.length === 0;
  return <SettingsSection title={t.title} description={t.description}>
    <form onSubmit={submit} className="flex flex-col gap-5">
      <FieldSet disabled={saving}>
        <Field orientation="horizontal">
          <Switch id={`${id}-enabled`} checked={draft.enabled} onCheckedChange={enabled => edit({ enabled })} disabled={saving} />
          <FieldLabel htmlFor={`${id}-enabled`}>{t.enabled}</FieldLabel>
        </Field>
        <FieldDescription>{t.cost}</FieldDescription>
        <FieldSet disabled={saving}>
          <FieldLegend>{t.characters}</FieldLegend>
          <div className="grid grid-cols-2 gap-3">
            {characters.map(character => <Field orientation="horizontal" key={character.id}>
              <Checkbox id={`${id}-${character.id}`} checked={draft.characters.includes(character.id)} onCheckedChange={checked => edit({ characters: checked ? [...draft.characters, character.id] : draft.characters.filter(c => c !== character.id) })} />
              <FieldLabel htmlFor={`${id}-${character.id}`}>{character.name}</FieldLabel>
            </Field>)}
          </div>
          {noCharacter && <FieldDescription role="alert">{t.selectRequired}</FieldDescription>}
        </FieldSet>
        <Field>
          <FieldLabel htmlFor={`${id}-interval`}>{t.interval}</FieldLabel>
          <Input id={`${id}-interval`} type="number" min={2} max={72} required value={draft.interval_hours} onChange={e => edit({ interval_hours: Number(e.target.value) })} />
          <FieldDescription>{t.intervalHint}</FieldDescription>
        </Field>
        <Field>
          <FieldLabel htmlFor={`${id}-limit`}>{t.limit}</FieldLabel>
          <Input id={`${id}-limit`} type="number" min={1} max={5} required value={draft.daily_limit} onChange={e => edit({ daily_limit: Number(e.target.value) })} />
          <FieldDescription>{t.limitHint}</FieldDescription>
        </Field>
        <FieldSet>
          <FieldLegend>{t.quiet}</FieldLegend>
          <FieldDescription>{t.quietHint}</FieldDescription>
          <FieldGroup className="sm:flex-row">
            <Field><FieldLabel htmlFor={`${id}-start`}>{t.quietStart}</FieldLabel><Input id={`${id}-start`} type="time" required value={draft.quiet_start} onChange={e => edit({ quiet_start: e.target.value })} /></Field>
            <Field><FieldLabel htmlFor={`${id}-end`}>{t.quietEnd}</FieldLabel><Input id={`${id}-end`} type="time" required value={draft.quiet_end} onChange={e => edit({ quiet_end: e.target.value })} /></Field>
          </FieldGroup>
        </FieldSet>
        <Field>
          <FieldLabel htmlFor={`${id}-timezone`}>{t.timezone}</FieldLabel>
          <Input id={`${id}-timezone`} required value={draft.timezone} onChange={e => edit({ timezone: e.target.value })} />
          <FieldDescription>{t.timezoneHint}</FieldDescription>
        </Field>
        <FieldDescription>{t.noReply}</FieldDescription>
      </FieldSet>
      {failure && <FailureNotice failure={failure} />}
      <div className="flex items-center gap-3"><Button type="submit" disabled={saving || noCharacter}>{t.save}</Button><span role="status">{saved ? t.saved : ""}</span></div>
    </form>
  </SettingsSection>;
}
