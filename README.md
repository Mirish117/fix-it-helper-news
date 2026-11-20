# fix-it-helper-news

A repository that feeds the **Fix-It Helper** IT tool, created by Mark Irish, with up-to-date news about drivers, Windows updates and known issues.

Fix-It Helper downloads `news.json` from this repository every time it opens, and again every 6 hours while it stays open. Each item is matched against the user's PC, so people only see "Affects this computer" for problems that really apply to them.

**Approved changes reach users right away.** Anything merged into `main` is live the next time someone opens the app. Review every pull request before you merge it.

## How news gets added

1. An automatic check runs twice a week (Wednesday and Saturday). It reads Microsoft's Windows release health pages and the NVIDIA, AMD and Intel driver release notes.
2. If it finds something new, it opens a **pull request** that changes `news.json`. If nothing changed, it does nothing.
3. A safety check (the "Check news list" action) runs on every pull request. It makes sure the file is valid and that no item does anything unsafe.
4. You read the pull request, then tap **Merge**. Users get the news the next time the app checks.

You can also edit `news.json` yourself on GitHub. Click the file, then the pencil icon, and choose "Create a new branch and start a pull request" so the safety check runs first.

## The format of news.json

```json
{
  "feedName": "Fix-It Helper News",
  "updated": "2026-11-20",
  "items": [
    {
      "id": "2026-11-short-unique-name",
      "date": "2026-11-12",
      "type": "problem",
      "title": "Short headline in plain words",
      "summary": "One to three sentences: what happened and who it affects.",
      "whatToDo": "Clear steps a non-technical person can follow.",
      "match": { "windows": "11", "versions": ["25H2", "26H2"] },
      "action": "run:winupdate",
      "actionLabel": "Open Windows Update",
      "source": "https://link-to-the-official-source",
      "sourceName": "Microsoft",
      "expires": "2027-02-01"
    }
  ]
}
```

- **updated**: change this to today's date whenever you edit the file. The app prefers the newest list.
- **date** and **expires**: use the `YYYY-MM-DD` format. Items are hidden after their `expires` date, and always after 180 days.
- **type**: `problem` (something is broken), `fixed` (a fix is available) or `info` (good to know).

### Matching items to a PC (all optional; every field you use must match)

| Field | Example | Meaning |
|---|---|---|
| `windows` | `"11"` | Windows 10 or 11 |
| `versions` | `["24H2", "25H2"]` | Windows 11 version |
| `editions` | `"^(Core\|Professional)"` | Windows edition. Core is Home, Professional is Pro |
| `gpu` | `"RTX 50"` | Text found in the graphics card name (regular expression) |
| `nvidiaDriverBelow` | `"621.14"` | NVIDIA driver is older than this |
| `missingUpdate` | `"KB5132061"` | This update is NOT installed |
| `hasUpdate` | `"KB5127936"` | This update IS installed |

An item with no `match` is shown to everyone as general news.

### Buttons (`action`)

For safety, the app only accepts these. Anything else is ignored, and the news list can never run commands on anyone's PC.

- `fix:internet`, `fix:cleanup`, `fix:graphics`, `fix:update`, `fix:windows`, `fix:apps`, `fix:virus`, `fix:explain`, `fix:sound`, `fix:printer`, `fix:taskbar`, `fix:clock`, `fix:bluetooth`. These open one of the app's own fixes.
- `run:winupdate`, `run:devmgmt`, `run:security`, `run:taskmgr`, `run:startup`, `run:power`, `run:explorer`, `run:mdsched`. These open a Windows settings page or tool.
- `url:https://...` opens a web page. Only `https` links are allowed.

## Writing good items

- Write for someone who is not good with computers. No jargon without a plain explanation.
- Only add things that are confirmed by Microsoft, NVIDIA, AMD or Intel, or reported by a well-known tech news site. Link the source.
- Keep the summary short, and write it in your own words. Do not copy text from the source article.
- Never tell people to turn off security features, edit the registry, or download tools from unofficial sites.
