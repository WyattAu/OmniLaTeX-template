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

export function activate(context: vscode.ExtensionContext) {
  console.log('OmniLaTeX extension activated');

  context.subscriptions.push(
    vscode.commands.registerCommand('omnilatex.pickDoctype', pickDoctype),
    vscode.commands.registerCommand('omnilatex.pickInstitution', pickInstitution),
    vscode.commands.registerCommand('omnilatex.pickLanguage', pickLanguage),
    vscode.commands.registerCommand('omnilatex.buildExample', buildCurrent),
    vscode.commands.registerCommand('omnilatex.buildAll', buildAll),
    vscode.commands.registerCommand('omnilatex.doctor', runDoctor),
  );
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
