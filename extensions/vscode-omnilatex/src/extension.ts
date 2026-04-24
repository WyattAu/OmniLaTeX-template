import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

const DOCTYPES = [
  { label: 'Thesis', value: 'thesis', description: 'Academic thesis (scrbook)' },
  { label: 'Dissertation', value: 'dissertation', description: 'Dissertation (scrbook)' },
  { label: 'Article', value: 'article', description: 'Standard article (scrartcl)' },
  { label: 'Journal', value: 'journal', description: 'Journal article (scrartcl)' },
  { label: 'CV', value: 'cv', description: 'Curriculum vitae (scrartcl)' },
  { label: 'Presentation', value: 'presentation', description: 'Presentation slides (scrartcl)' },
  { label: 'Poster', value: 'poster', description: 'Conference poster (scrartcl)' },
  { label: 'Letter', value: 'letter', description: 'Formal letter (scrartcl)' },
  { label: 'Book', value: 'book', description: 'Book (scrbook)' },
  { label: 'Manual', value: 'manual', description: 'Manual/handbook (scrreprt)' },
  { label: 'Technical Report', value: 'technicalreport', description: 'Technical report (scrreprt)' },
  { label: 'Standard', value: 'standard', description: 'Standards document (scrreprt)' },
  { label: 'Patent', value: 'patent', description: 'Patent application (scrreprt)' },
  { label: 'Cover Letter', value: 'cover-letter', description: 'Cover letter (scrartcl)' },
  { label: 'Dictionary', value: 'dictionary', description: 'Dictionary/lexicon (scrbook)' },
  { label: 'Inline Paper', value: 'inlinepaper', description: 'Inline research paper (scrartcl)' },
];

const LANGUAGES = [
  'english', 'german', 'french', 'spanish', 'portuguese', 'italian',
  'dutch', 'russian', 'chinese', 'japanese', 'korean', 'arabic',
];

let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
  console.log('OmniLaTeX extension activated');

  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.command = 'omnilatex.pickDoctype';
  context.subscriptions.push(statusBarItem);
  updateStatusBar();

  context.subscriptions.push(
    vscode.commands.registerCommand('omnilatex.pickDoctype', pickDoctype),
    vscode.commands.registerCommand('omnilatex.pickInstitution', pickInstitution),
    vscode.commands.registerCommand('omnilatex.pickLanguage', pickLanguage),
    vscode.commands.registerCommand('omnilatex.buildExample', buildCurrent),
    vscode.commands.registerCommand('omnilatex.buildAll', buildAll),
    vscode.commands.registerCommand('omnilatex.doctor', runDoctor),
    vscode.commands.registerCommand('omnilatex.createProject', createProject),
  );

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(updateStatusBar),
    vscode.workspace.onDidChangeTextDocument(() => updateStatusBar()),
  );

  showWelcomeMessage(context);
}

function showWelcomeMessage(context: vscode.ExtensionContext) {
  const key = 'omnilatex.welcomed';
  const welcomed = context.globalState.get<boolean>(key, false);
  if (!welcomed) {
    context.globalState.update(key, true);
    vscode.window.showInformationMessage(
      'OmniLaTeX extension activated! Use the OmniLaTeX commands to get started.',
      'Open Commands'
    ).then(choice => {
      if (choice === 'Open Commands') {
        vscode.commands.executeCommand('workbench.action.showCommands');
      }
    });
  }
}

function parseDocumentOptions(text: string): { doctype: string; language: string; institution: string } {
  const match = text.match(/\\documentclass\s*\[([\s\S]*?)\]\{omnilatex\}/);
  const result = { doctype: '—', language: '—', institution: '—' };
  if (!match) { return result; }
  const opts = match[1];
  const dt = opts.match(/doctype=(\w+)/);
  const lg = opts.match(/language=(\w+)/);
  const inst = opts.match(/institution=(\w+)/);
  if (dt) { result.doctype = dt[1]; }
  if (lg) { result.language = lg[1]; }
  if (inst) { result.institution = inst[1]; }
  return result;
}

function updateStatusBar() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    statusBarItem.hide();
    return;
  }
  const text = editor.document.getText();
  const opts = parseDocumentOptions(text);
  if (opts.doctype === '—' && !text.includes('omnilatex')) {
    statusBarItem.hide();
    return;
  }
  statusBarItem.text = `$(book) ${opts.doctype}  |  $(globe) ${opts.language}  |  $(organization) ${opts.institution}`;
  statusBarItem.tooltip = 'OmniLaTeX: Click to change document type';
  statusBarItem.show();
}

async function createProject() {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  const workspaceRoot = workspaceFolders ? workspaceFolders[0].uri.fsPath : undefined;

  if (!workspaceRoot) {
    vscode.window.showErrorMessage('Please open a workspace folder first.');
    return;
  }

  const buildPy = path.join(workspaceRoot, 'build.py');
  if (!fs.existsSync(buildPy)) {
    vscode.window.showErrorMessage(`build.py not found at ${buildPy}. Make sure you are in an OmniLaTeX workspace.`);
    return;
  }

  const name = await vscode.window.showInputBox({
    prompt: 'Enter project name',
    placeHolder: 'my-thesis',
    validateInput: (value) => {
      if (!value || !/^[a-zA-Z0-9_-]+$/.test(value)) {
        return 'Project name must contain only letters, numbers, hyphens, and underscores.';
      }
      return undefined;
    },
  });
  if (!name) { return; }

  const defaultDoctype = vscode.workspace.getConfiguration('omnilatex').get<string>('defaultDoctype', 'thesis');
  const defaultLanguage = vscode.workspace.getConfiguration('omnilatex').get<string>('defaultLanguage', 'english');

  const terminal = vscode.window.createTerminal('OmniLaTeX Create');
  terminal.show();
  terminal.sendText(`python3 build.py init ${name} --doctype ${defaultDoctype} --language ${defaultLanguage}`);
}

async function pickDoctype() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) { return; }
  
  const pick = await vscode.window.showQuickPick(DOCTYPES, {
    placeHolder: 'Select document type...',
  });
  if (!pick) { return; }
  
  const doc = editor.document;
  const text = doc.getText();
  const regex = /(\\documentclass\s*\[)([\s\S]*?)(\]\{omnilatex\})/;
  const match = text.match(regex);
  if (match) {
    let options = match[2].replace(/doctype=\w+/g, '').trim();
    options = options ? `doctype=${pick.value}, ${options}` : `doctype=${pick.value}`;
    const newText = text.replace(regex, `$1${options}$3`);
    const fullRange = new vscode.Range(
      doc.positionAt(0), doc.positionAt(text.length)
    );
    editor.edit(editBuilder => {
      editBuilder.replace(fullRange, newText);
    });
    vscode.window.showInformationMessage(`Document type changed to: ${pick.label}`);
  } else {
    vscode.window.showErrorMessage('Could not find \\documentclass{omnilatex} in current file');
  }
}

async function pickInstitution() {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  if (!workspaceFolders) { return; }
  
  const instDir = path.join(workspaceFolders[0].uri.fsPath, 'config', 'institutions');
  let institutions: string[] = ['none'];
  
  if (fs.existsSync(instDir)) {
    institutions = institutions.concat(
      fs.readdirSync(instDir, { withFileTypes: true })
        .filter(d => d.isDirectory() && d.name !== 'README.md')
        .map(d => d.name)
    );
  }
  
  const pick = await vscode.window.showQuickPick(
    institutions.map(i => ({ label: i === 'none' ? 'None (generic)' : i.charAt(0).toUpperCase() + i.slice(1), value: i })),
    { placeHolder: 'Select institution...' }
  );
  if (!pick) { return; }
  
  const editor = vscode.window.activeTextEditor;
  if (!editor) { return; }
  
  const doc = editor.document;
  const text = doc.getText();
  const regex = /(\\documentclass\s*\[)([\s\S]*?)(\]\{omnilatex\})/;
  const match = text.match(regex);
  if (match) {
    let options = match[2].replace(/institution=\w+/g, '').trim();
    options = options ? `institution=${pick.value}, ${options}` : `institution=${pick.value}`;
    const newText = text.replace(regex, `$1${options}$3`);
    const fullRange = new vscode.Range(doc.positionAt(0), doc.positionAt(text.length));
    editor.edit(editBuilder => { editBuilder.replace(fullRange, newText); });
    vscode.window.showInformationMessage(`Institution changed to: ${pick.label}`);
  }
}

async function pickLanguage() {
  const pick = await vscode.window.showQuickPick(
    LANGUAGES.map(l => ({ label: l.charAt(0).toUpperCase() + l.slice(1), value: l })),
    { placeHolder: 'Select language...' }
  );
  if (!pick) { return; }
  
  const editor = vscode.window.activeTextEditor;
  if (!editor) { return; }
  
  const doc = editor.document;
  const text = doc.getText();
  const regex = /(\\documentclass\s*\[)([\s\S]*?)(\]\{omnilatex\})/;
  const match = text.match(regex);
  if (match) {
    let options = match[2].replace(/language=\w+/g, '').trim();
    options = options ? `language=${pick.value}, ${options}` : `language=${pick.value}`;
    const newText = text.replace(regex, `$1${options}$3`);
    const fullRange = new vscode.Range(doc.positionAt(0), doc.positionAt(text.length));
    editor.edit(editBuilder => { editBuilder.replace(fullRange, newText); });
    vscode.window.showInformationMessage(`Language changed to: ${pick.label}`);
  }
}

function runBuildCommand(command: string) {
  const terminal = vscode.window.createTerminal('OmniLaTeX Build');
  terminal.show();
  terminal.sendText(`python3 build.py ${command}`);
}

function buildCurrent() {
  const editor = vscode.window.activeTextEditor;
  if (editor) {
    const fileName = path.basename(editor.document.uri.fsPath, '.tex');
    runBuildCommand(`build-example ${fileName}`);
  } else {
    runBuildCommand('build-root');
  }
}

function buildAll() { runBuildCommand('build-examples'); }
function runDoctor() { runBuildCommand('doctor'); }

export function deactivate() {}
