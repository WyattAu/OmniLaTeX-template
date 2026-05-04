import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';

const DOCTYPES: string[] = [
    'article', 'book', 'cover-letter', 'cv', 'dictionary', 'dissertation',
    'exam', 'handout', 'homework', 'inlinepaper', 'invoice', 'journal',
    'lecture-notes', 'letter', 'manual', 'memo', 'patent', 'poster',
    'presentation', 'recipe', 'research-proposal', 'standard', 'syllabus',
    'technicalreport', 'thesis', 'white-paper'
];

const INSTITUTIONS: string[] = [
    'cambridge', 'cmu', 'epfl', 'eth', 'generic', 'harvard', 'imperial',
    'mit', 'none', 'oxford', 'princeton', 'stanford', 'tudelft', 'tuhh',
    'tum', 'yale'
];

const LANGUAGES: string[] = [
    'english', 'german', 'french', 'spanish', 'russian', 'italian',
    'portuguese', 'dutch', 'polish', 'czech', 'greek', 'turkish',
    'simplifiedchinese', 'traditionalchinese', 'japanese', 'korean',
    'arabic', 'hebrew', 'persian'
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
        'thesis', 'dissertation', 'article', 'journal', 'research-proposal',
        'technicalreport', 'lecture-notes', 'syllabus', 'homework', 'exam', 'handout'
    ],
    Business: ['invoice', 'memo', 'cover-letter', 'standard', 'patent', 'manual'],
    Personal: ['cv', 'letter', 'book', 'dictionary', 'poster', 'presentation', 'white-paper', 'recipe']
};

const DOCTYPE_DESCRIPTIONS: Record<string, string> = {
    'article': 'Standard article (scrartcl)',
    'book': 'Book (scrbook)',
    'cover-letter': 'Cover letter (scrartcl)',
    'cv': 'Curriculum vitae (scrartcl)',
    'dictionary': 'Dictionary/lexicon (scrbook)',
    'dissertation': 'Dissertation (scrbook)',
    'exam': 'Exam document (scrartcl)',
    'handout': 'Handout (scrartcl)',
    'homework': 'Homework assignment (scrartcl)',
    'inlinepaper': 'Inline research paper (scrartcl)',
    'invoice': 'Invoice (scrartcl)',
    'journal': 'Journal article (scrartcl)',
    'lecture-notes': 'Lecture notes (scrartcl)',
    'letter': 'Formal letter (scrartcl)',
    'manual': 'Manual/handbook (scrreprt)',
    'memo': 'Memo (scrartcl)',
    'patent': 'Patent application (scrreprt)',
    'poster': 'Conference poster (scrartcl)',
    'presentation': 'Presentation slides (scrartcl)',
    'recipe': 'Recipe (scrartcl)',
    'research-proposal': 'Research proposal (scrartcl)',
    'standard': 'Standards document (scrreprt)',
    'syllabus': 'Syllabus (scrartcl)',
    'technicalreport': 'Technical report (scrreprt)',
    'thesis': 'Academic thesis (scrbook)',
    'white-paper': 'White paper (scrartcl)'
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
            .filter(f => f.endsWith('.tex'))
            .map(f => path.basename(f, '.tex'));
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
            exec(`python3 "${buildPy}" build-example ${exampleName}`, { cwd: root }, (error) => {
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
            exec(`python3 "${buildPy}" build-all`, { cwd: root }, (error) => {
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
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('omnilatex')) {
                updateStatusBar();
            }
        })
    );

    updateStatusBar();
}

export function deactivate() {}
