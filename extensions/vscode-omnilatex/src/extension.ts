import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';

let logDiagnostics: vscode.DiagnosticCollection | undefined;

function spawnAsync(command: string, args: string[], options: { cwd: string }): Promise<{ error: Error | null; stdout: string; stderr: string }> {
    return new Promise((resolve) => {
        const proc = spawn(command, args, options);
        let stdout = '';
        let stderr = '';
        proc.stdout?.on('data', (data: Buffer) => { stdout += data.toString(); });
        proc.stderr?.on('data', (data: Buffer) => { stderr += data.toString(); });
        proc.on('error', (err) => { resolve({ error: err, stdout, stderr }); });
        proc.on('close', (code) => {
            if (code !== 0) {
                resolve({ error: new Error(`Process exited with code ${code}`), stdout, stderr });
            } else {
                resolve({ error: null, stdout, stderr });
            }
        });
    });
}

const DOCTYPES: string[] = [
    'annotated-bibliography', 'annual-report', 'api-reference', 'article',
    'beamer', 'blog-post', 'book', 'book-chapter', 'brochure',
    'business-letter', 'case-study', 'changelog', 'chapter',
    'conference-proceedings', 'cover-letter', 'course-material',
    'course-notes', 'cv', 'dictionary', 'dissertation', 'exam',
    'grant-proposal', 'handbook', 'handout', 'homework', 'ieee',
    'inlinepaper', 'invitation', 'invoice', 'journal', 'lab-report',
    'lecture-notes', 'legislation', 'letter', 'literature-review',
    'manual', 'meeting-minutes', 'memo', 'newsletter', 'patent',
    'poster', 'preprint', 'presentation', 'proceedings', 'program',
    'product-spec', 'quiz', 'recipe', 'regulation', 'report',
    'research-proposal', 'software-documentation', 'standard',
    'strategic-plan', 'syllabus', 'technical-spec', 'technicalreport',
    'textbook', 'thesis', 'thesis-proposal', 'white-paper',
    'working-paper'
];

const INSTITUTIONS: string[] = [
    'aalto', 'berkeley', 'brown', 'caltech', 'cambridge', 'chalmers',
    'cmu', 'cornell', 'columbia', 'dartmouth', 'epfl', 'eth',
    'gatech', 'generic', 'harvard', 'imperial', 'johnshopkins', 'kit',
    'mit', 'none', 'ntnu', 'oxford', 'princeton', 'stanford',
    'tudelft', 'tuhh', 'tum', 'uoft', 'umich', 'upenn', 'wisc', 'yale'
];

const LANGUAGES: string[] = [
    'english', 'german', 'french', 'spanish', 'russian', 'italian',
    'portuguese', 'dutch', 'polish', 'czech', 'greek', 'turkish',
    'simplifiedchinese', 'traditionalchinese', 'japanese', 'korean',
    'arabic', 'hebrew', 'persian', 'bengali', 'hindi', 'thai',
    'vietnamese', 'ukrainian', 'bulgarian', 'croatian', 'serbian',
    'slovak', 'slovenian', 'romanian', 'catalan', 'mongolian'
];

const COLOR_MODES: string[] = ['dark', 'light', 'auto'];
const LINK_STYLES: string[] = ['default', 'plain'];
const CODE_STYLES: string[] = ['default', 'plain'];

const CLASS_OPTIONS = [
    { name: 'doctype', description: 'Document type' },
    { name: 'institution', description: 'Institution' },
    { name: 'language', description: 'Language' },
    { name: 'color-mode', description: 'Color mode (dark/light/auto)' },
    { name: 'link-style', description: 'Link style (default/plain)' },
    { name: 'code-style', description: 'Code style (default/plain)' }
];

const DOCTYPE_CATEGORIES: Record<string, string[]> = {
    Academic: [
        'thesis', 'dissertation', 'thesis-proposal', 'article', 'journal',
        'research-proposal', 'technicalreport', 'lecture-notes', 'syllabus',
        'homework', 'exam', 'handout', 'book-chapter', 'grant-proposal',
        'lab-report', 'literature-review', 'annotated-bibliography',
        'preprint', 'working-paper', 'proceedings'
    ],
    Business: [
        'invoice', 'memo', 'cover-letter', 'business-letter', 'standard',
        'patent', 'manual', 'report', 'ieee', 'meeting-minutes',
        'quarterly-report', 'strategic-plan', 'product-spec', 'annual-report'
    ],
    Education: [
        'course-material', 'course-notes', 'textbook', 'quiz', 'lesson-plan'
    ],
    Technical: [
        'software-documentation', 'api-reference', 'changelog', 'technical-spec'
    ],
    Creative: [
        'blog-post', 'newsletter', 'brochure', 'invitation', 'program',
        'recipe', 'white-paper', 'case-study'
    ],
    Government: [
        'legislation', 'regulation'
    ],
    Personal: [
        'cv', 'letter', 'book', 'guide', 'handbook', 'dictionary',
        'poster', 'presentation'
    ]
};

const DOCTYPE_DESCRIPTIONS: Record<string, string> = {
    'annotated-bibliography': 'Annotated bibliography (scrartcl)',
    'annual-report': 'Annual report (scrreprt)',
    'api-reference': 'API reference documentation (scrreprt)',
    'article': 'Standard article (scrartcl)',
    'beamer': 'Presentation slides (beamer)',
    'blog-post': 'Blog post / web article (scrartcl)',
    'book': 'Book (scrbook)',
    'book-chapter': 'Individual book chapter (scrartcl)',
    'brochure': 'Brochure / flyer (scrartcl)',
    'business-letter': 'Formal business letter (scrartcl)',
    'case-study': 'Case study analysis (scrartcl)',
    'changelog': 'Changelog / release notes (scrartcl)',
    'cover-letter': 'Cover letter (scrartcl)',
    'course-material': 'Course material / syllabus (scrreprt)',
    'course-notes': 'Lecture / course notes (scrartcl)',
    'cv': 'Curriculum vitae (scrartcl)',
    'dictionary': 'Dictionary/lexicon (scrbook)',
    'dissertation': 'Dissertation (scrbook)',
    'exam': 'Exam / test document (scrartcl)',
    'grant-proposal': 'Grant proposal (NSF/ERC style, scrartcl)',
    'guide': 'Guidebook (scrbook)',
    'handbook': 'Handbook (scrbook)',
    'handout': 'Handout (scrartcl)',
    'homework': 'Homework assignment (scrartcl)',
    'ieee': 'IEEE conference paper (two-column, scrartcl)',
    'inlinepaper': 'Inline research paper (scrartcl)',
    'invitation': 'Event invitation (scrartcl)',
    'invoice': 'Invoice (scrartcl)',
    'journal': 'Journal article (scrartcl)',
    'lab-report': 'Laboratory report (scrartcl)',
    'lecture-notes': 'Lecture notes (scrartcl)',
    'legislation': 'Legislation / act (scrreprt)',
    'letter': 'Formal letter (scrartcl)',
    'literature-review': 'Literature review (scrartcl)',
    'manual': 'Manual / handbook (scrreprt)',
    'meeting-minutes': 'Meeting minutes (scrartcl)',
    'memo': 'Memo (scrartcl)',
    'newsletter': 'Newsletter (scrartcl)',
    'patent': 'Patent application (scrreprt)',
    'poster': 'Conference poster (scrartcl)',
    'preprint': 'Preprint paper (scrartcl)',
    'presentation': 'Presentation slides (scrartcl)',
    'proceedings': 'Conference proceedings (scrbook)',
    'program': 'Event programme (scrartcl)',
    'product-spec': 'Product specification (scrreprt)',
    'quiz': 'Quiz / test (scrartcl)',
    'recipe': 'Recipe (scrartcl)',
    'regulation': 'Regulation document (scrreprt)',
    'report': 'Report (scrreprt)',
    'research-proposal': 'Research proposal (scrartcl)',
    'software-documentation': 'Software documentation (scrreprt)',
    'standard': 'Standards document (scrreprt)',
    'strategic-plan': 'Strategic plan (scrreprt)',
    'syllabus': 'Syllabus (scrartcl)',
    'technical-spec': 'Technical specification (scrreprt)',
    'technicalreport': 'Technical report (scrreprt)',
    'textbook': 'Textbook (scrbook)',
    'thesis': 'Academic thesis (scrbook)',
    'thesis-proposal': 'Thesis proposal / prospectus (scrreprt)',
    'white-paper': 'White paper (scrartcl)',
    'working-paper': 'Working / discussion paper (scrartcl)'
};

class OmniLaTeXCompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        _token: vscode.CancellationToken,
        _context: vscode.CompletionContext
    ): vscode.ProviderResult<vscode.CompletionItem[]> {
        const textBefore = document.getText(new vscode.Range(new vscode.Position(0, 0), position));

        const docClassRegex = /\\documentclass\s*\[/g;
        let lastMatch: RegExpExecArray | null = null;
        let match: RegExpExecArray | null;
        while ((match = docClassRegex.exec(textBefore)) !== null) {
            lastMatch = match;
        }

        if (!lastMatch) {
            return undefined;
        }

        const bracketStartIndex = lastMatch.index + lastMatch[0].length - 1;
        const textAfterBracket = textBefore.substring(bracketStartIndex + 1);
        if (textAfterBracket.includes(']')) {
            return undefined;
        }

        const lastCommaIndex = textAfterBracket.lastIndexOf(',');
        const currentSegment = textAfterBracket.substring(lastCommaIndex + 1).trim();

        const eqIndex = currentSegment.indexOf('=');
        if (eqIndex !== -1) {
            const optionName = currentSegment.substring(0, eqIndex).trim();
            const partialValue = currentSegment.substring(eqIndex + 1).trim();
            return this.getOptionValues(optionName, partialValue);
        }

        return this.getOptionNames(currentSegment);
    }

    private getOptionNames(partial: string): vscode.CompletionItem[] {
        return CLASS_OPTIONS
            .filter(o => o.name.startsWith(partial))
            .map(o => {
                const item = new vscode.CompletionItem(o.name + '=', vscode.CompletionItemKind.Property);
                item.detail = o.description;
                item.insertText = o.name + '=';
                item.sortText = o.name;
                return item;
            });
    }

    private getOptionValues(optionName: string, partialValue: string): vscode.CompletionItem[] | undefined {
        let values: string[] | undefined;
        switch (optionName) {
            case 'doctype':
                values = DOCTYPES;
                break;
            case 'institution':
                values = INSTITUTIONS;
                break;
            case 'language':
                values = LANGUAGES;
                break;
            case 'color-mode':
                values = COLOR_MODES;
                break;
            case 'link-style':
                values = LINK_STYLES;
                break;
            case 'code-style':
                values = CODE_STYLES;
                break;
            default:
                return undefined;
        }

        return values!
            .filter(v => v.startsWith(partialValue))
            .map(v => {
                const item = new vscode.CompletionItem(v, vscode.CompletionItemKind.EnumMember);
                if (optionName === 'doctype' && DOCTYPE_DESCRIPTIONS[v]) {
                    item.detail = DOCTYPE_DESCRIPTIONS[v];
                }
                item.sortText = v;
                return item;
            });
    }
}

function parseDocumentOptions(text: string): { doctype: string; institution: string } {
    const match = text.match(/\\documentclass\s*\[([\s\S]*?)\]\s*\{omnilatex\}/);
    const result = { doctype: '', institution: '' };
    if (!match) { return result; }
    const opts = match[1];
    const dt = opts.match(/doctype=([a-zA-Z-]+)/);
    const inst = opts.match(/institution=([a-zA-Z-]+)/);
    if (dt) { result.doctype = dt[1]; }
    if (inst) { result.institution = inst[1]; }
    return result;
}

function replaceOption(text: string, optionName: string, newValue: string): string | undefined {
    const regex = /(\\documentclass\s*\[)([\s\S]*?)(\]\s*\{omnilatex\})/;
    const match = text.match(regex);
    if (!match) { return undefined; }

    const cleaned = match[2]
        .replace(new RegExp(`${optionName}=[\\w-]+`, 'g'), '')
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0)
        .join(', ');

    const options = cleaned ? `${optionName}=${newValue}, ${cleaned}` : `${optionName}=${newValue}`;
    return text.replace(regex, `$1${options}$3`);
}

function findWorkspaceRoot(): string | undefined {
    const folders = vscode.workspace.workspaceFolders;
    if (!folders) { return undefined; }

    for (const folder of folders) {
        const p = folder.uri.fsPath;
        if (fs.existsSync(path.join(p, 'omnilatex.cls')) || fs.existsSync(path.join(p, 'build.py'))) {
            return p;
        }
    }

    return folders[0]?.uri.fsPath;
}

function getExampleNames(root: string): string[] {
    const examplesDir = path.join(root, 'examples');
    if (!fs.existsSync(examplesDir)) { return []; }
    try {
        return fs.readdirSync(examplesDir)
            .filter(f => {
                const full = path.join(examplesDir, f);
                return fs.statSync(full).isDirectory() && fs.existsSync(path.join(full, 'main.tex'));
            })
            .sort();
    } catch {
        return [];
    }
}

async function switchDoctype(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) { return; }

    const items: vscode.QuickPickItem[] = [];
    for (const [category, doctypes] of Object.entries(DOCTYPE_CATEGORIES)) {
        items.push({ label: category, kind: vscode.QuickPickItemKind.Separator });
        for (const dt of doctypes) {
            items.push({ label: dt, description: DOCTYPE_DESCRIPTIONS[dt] || '' });
        }
    }

    const pick = await vscode.window.showQuickPick(items, { placeHolder: 'Select document type...' });
    if (!pick || pick.kind === vscode.QuickPickItemKind.Separator) { return; }

    const doc = editor.document;
    const text = doc.getText();
    const newText = replaceOption(text, 'doctype', pick.label);
    if (!newText) {
        vscode.window.showErrorMessage('Could not find \\documentclass{omnilatex} in current file');
        return;
    }

    const fullRange = new vscode.Range(doc.positionAt(0), doc.positionAt(text.length));
    await editor.edit(editBuilder => editBuilder.replace(fullRange, newText));
    vscode.window.showInformationMessage(`Document type changed to: ${pick.label}`);
}

async function switchInstitution(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) { return; }

    const pick = await vscode.window.showQuickPick(
        INSTITUTIONS.map(i => ({
            label: i === 'none' ? 'None (generic)' : i.charAt(0).toUpperCase() + i.slice(1),
            value: i
        })),
        { placeHolder: 'Select institution...' }
    );
    if (!pick) { return; }

    const doc = editor.document;
    const text = doc.getText();
    const newText = replaceOption(text, 'institution', pick.value);
    if (!newText) {
        vscode.window.showErrorMessage('Could not find \\documentclass{omnilatex} in current file');
        return;
    }

    const fullRange = new vscode.Range(doc.positionAt(0), doc.positionAt(text.length));
    await editor.edit(editBuilder => editBuilder.replace(fullRange, newText));
    vscode.window.showInformationMessage(`Institution changed to: ${pick.label}`);
}

async function buildExample(): Promise<void> {
    const root = findWorkspaceRoot();
    if (!root) {
        vscode.window.showErrorMessage('Could not find OmniLaTeX workspace root');
        return;
    }

    const examples = getExampleNames(root);
    let exampleName: string | undefined;

    if (examples.length > 0) {
        exampleName = await vscode.window.showQuickPick(examples, { placeHolder: 'Select example to build...' });
    } else {
        exampleName = await vscode.window.showInputBox({ prompt: 'Enter example name to build', placeHolder: 'thesis' });
    }
    if (!exampleName) { return; }

    const buildPy = path.join(root, 'build.py');
    await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: `Building ${exampleName}...` },
        () => new Promise<void>((resolve) => {
            spawnAsync('python3', [buildPy, 'build-example', exampleName], { cwd: root }).then(({ error }) => {
                if (error) {
                    vscode.window.showErrorMessage(`Build failed: ${error.message}`);
                } else {
                    vscode.window.showInformationMessage(`Built ${exampleName} successfully`);
                }
                resolve();
            });
        })
    );
}

async function buildAll(): Promise<void> {
    const root = findWorkspaceRoot();
    if (!root) {
        vscode.window.showErrorMessage('Could not find OmniLaTeX workspace root');
        return;
    }

    const buildPy = path.join(root, 'build.py');
    await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: 'Building all examples...' },
        () => new Promise<void>((resolve) => {
            spawnAsync('python3', [buildPy, 'build-all'], { cwd: root }).then(({ error }) => {
                if (error) {
                    vscode.window.showErrorMessage(`Build failed: ${error.message}`);
                } else {
                    vscode.window.showInformationMessage('All examples built successfully');
                }
                resolve();
            });
        })
    );
}

export function activate(context: vscode.ExtensionContext): void {
    const statusItem = vscode.languages.createLanguageStatusItem('omnilatex', ['latex', 'latex-expl3']);
    statusItem.text = 'OmniLaTeX';
    statusItem.command = { command: 'omnilatex.switchDoctype', title: 'Switch Document Type' };
    context.subscriptions.push(statusItem);

    const updateStatusBar = () => {
        const cfg = vscode.workspace.getConfiguration('omnilatex');
        if (!cfg.get<boolean>('statusBar.show', true)) {
            statusItem.text = '';
            statusItem.detail = undefined;
            return;
        }
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            statusItem.text = 'OmniLaTeX';
            statusItem.detail = undefined;
            return;
        }
        const text = editor.document.getText();
        const opts = parseDocumentOptions(text);
        if (!opts.doctype && !text.includes('omnilatex')) {
            statusItem.text = 'OmniLaTeX';
            statusItem.detail = undefined;
            return;
        }
        statusItem.text = 'OmniLaTeX';
        statusItem.detail = opts.doctype
            ? opts.institution
                ? `${opts.doctype} | ${opts.institution}`
                : opts.doctype
            : undefined;
    };

    const completionProvider = new OmniLaTeXCompletionProvider();
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            ['latex', 'latex-expl3'],
            completionProvider,
            '[', ',', '='
        ),
        vscode.commands.registerCommand('omnilatex.switchDoctype', switchDoctype),
        vscode.commands.registerCommand('omnilatex.switchInstitution', switchInstitution),
        vscode.commands.registerCommand('omnilatex.build', buildExample),
        vscode.commands.registerCommand('omnilatex.buildAll', buildAll),
        vscode.window.onDidChangeActiveTextEditor(updateStatusBar),
        vscode.workspace.onDidChangeTextDocument(updateStatusBar),
        vscode.workspace.onDidSaveTextDocument(async (document) => {
            const cfg = vscode.workspace.getConfiguration('omnilatex');
            if (!cfg.get<boolean>('buildOnSave', false)) { return; }
            if (!document.fileName.endsWith('.tex')) { return; }

            const root = findWorkspaceRoot();
            if (!root) { return; }

            const outputChannel = vscode.window.createOutputChannel('OmniLaTeX Build');
            outputChannel.show(true);
            outputChannel.appendLine(`[build-on-save] Building ${document.fileName}...`);

            await vscode.window.withProgress(
                { location: vscode.ProgressLocation.Notification, title: 'Building on save...' },
                () => new Promise<void>((resolve) => {
                    const cwd = path.dirname(document.fileName);
                    spawnAsync('latexmk', ['-lualatex', '-interaction=nonstopmode', document.fileName], { cwd }).then(({ error, stdout, stderr }) => {
                            if (stdout) { outputChannel.append(stdout); }
                            if (stderr) { outputChannel.append(stderr); }
                            if (error) {
                                vscode.window.showErrorMessage(`Build on save failed: ${error.message}`);
                            } else {
                                outputChannel.appendLine('[build-on-save] Build succeeded.');
                            }
                            resolve();
                        });
                })
            );
        }),
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('omnilatex')) {
                updateStatusBar();
            }
        })
    );

    updateStatusBar();

    // LaTeX log file diagnostic provider
    logDiagnostics = vscode.languages.createDiagnosticCollection('latex-log');
    context.subscriptions.push(logDiagnostics);

    function parseLatexErrors(logContent: string): vscode.Diagnostic[] {
        const diagnostics: vscode.Diagnostic[] = [];
        const lines = logContent.split('\n');
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            // Undefined control sequence
            if (/^!\s+Undefined control sequence\.?\s*$/.test(line)) {
                const cmd = (i + 1 < lines.length)
                    ? (lines[i + 1].match(/<recently read>\s+(\\?\S+)/) || [])[1] || ''
                    : '';
                const msg = cmd ? `Undefined command: ${cmd}` : 'Undefined control sequence';
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    msg, vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // LaTeX Error (check before generic "!")
            if (/^!\s+LaTeX Error:\s*(.+)$/.test(line)) {
                const m = line.match(/^!\s+LaTeX Error:\s*(.+)$/);
                let msg = m?.[1] || line;
                // File not found
                const fnf = line.match(/File `([^']+)' not found/);
                if (fnf) { msg = `File '${fnf[1]}' not found`; }
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    `LaTeX Error: ${msg}`, vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Package error
            if (/^!\s+Package \S+ Error:/.test(line)) {
                const m = line.match(/^!\s+Package (\S+) Error:\s*(.+)$/);
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    `[${m?.[1] || 'package'}] ${m?.[2] || line}`,
                    vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Missing $ inserted
            if (/^!\s+Missing \$ inserted/.test(line)) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    'Missing $ inserted (math mode required here)',
                    vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Missing brace
            const braceM = line.match(/^!\s+Missing ([{}]) inserted/);
            if (braceM) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    `Missing '${braceM[1]}' inserted`,
                    vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Missing endgroup/endcsname
            if (/^!\s+Missing \\end(group|csname) inserted/.test(line)) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    line.replace(/^!\s+/, '').replace(/\.?\s*$/, ''),
                    vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Invalid character
            if (/^!\s+Text line contains an invalid character/.test(line)) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    'Text line contains an invalid character',
                    vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Dimension / number / alignment errors
            if (/^!\s+(Illegal unit of measure|Missing number|Misplaced alignment tab)/.test(line)) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    line.replace(/^!\s+/, '').replace(/\.?\s*$/, ''),
                    vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Runaway argument
            if (/^!\s+Runaway argument/.test(line)) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    'Runaway argument (unclosed macro argument)',
                    vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Generic "!" error (catch-all, must be after specific patterns)
            const genericM = line.match(/^!\s+(.+?)\.?\s*$/);
            if (genericM && line.startsWith('!')) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    `LaTeX: ${genericM[1]}`, vscode.DiagnosticSeverity.Error,
                ));
                continue;
            }

            // Package warning
            const warnM = line.match(/^Package\s+(\S+)\s+Warning:\s*(.+)$/);
            if (warnM) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    `[${warnM[1]}] ${warnM[2]}`, vscode.DiagnosticSeverity.Warning,
                ));
                continue;
            }

            // LaTeX warning
            const latexWarnM = line.match(/^LaTeX Warning:\s*(.+)$/);
            if (latexWarnM) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    `LaTeX Warning: ${latexWarnM[1]}`, vscode.DiagnosticSeverity.Warning,
                ));
                continue;
            }

            // Overfull/Underfull hbox
            if (/^(Overfull|Underfull)\s+\\hbox/.test(line)) {
                diagnostics.push(new vscode.Diagnostic(
                    new vscode.Range(i, 0, i, line.length),
                    line.trim(), vscode.DiagnosticSeverity.Warning,
                ));
                continue;
            }
        }
        return diagnostics;
    }

    // Update diagnostics when active editor changes
    async function updateLogDiagnostics(document: vscode.TextDocument) {
        if (document.languageId !== 'latex' && !document.fileName.endsWith('.tex')) {
            return;
        }
        const logPath = document.fileName.replace(/\.tex$/, '.log');
        const logUri = vscode.Uri.file(logPath);
        try {
            const content = await vscode.workspace.fs.readFile(logUri);
            const diagnostics = parseLatexErrors(content.toString());
            logDiagnostics.set(document.uri, diagnostics);
        } catch {
            // .log file may not exist yet, silently ignore
        }
    }

    vscode.workspace.onDidSaveTextDocument(updateLogDiagnostics);
    vscode.workspace.onDidOpenTextDocument(updateLogDiagnostics);
}

export function deactivate() {
    if (logDiagnostics) {
        logDiagnostics.dispose();
        logDiagnostics = undefined;
    }
}
