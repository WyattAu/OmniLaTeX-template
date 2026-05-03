const vscode = require('vscode');

const DOCUMENT_TYPES = [
  'article', 'book', 'cover-letter', 'cv', 'dictionary', 'dissertation',
  'exam', 'handout', 'homework', 'inlinepaper', 'invoice', 'journal',
  'lecture-notes', 'letter', 'manual', 'memo', 'patent', 'poster',
  'presentation', 'research-proposal', 'standard', 'syllabus', 'technicalreport',
  'thesis', 'white-paper'
];

const INSTITUTIONS = [
  'cambridge', 'cmu', 'epfl', 'eth', 'generic', 'imperial', 'mit',
  'oxford', 'princeton', 'stanford', 'tudelft', 'tuhh', 'tum', 'yale'
];

function activate(context) {
  console.log('OmniLaTeX extension activated');

  const switchDoctype = vscode.commands.registerCommand('omnilatex.switchDoctype', async () => {
    const picked = await vscode.window.showQuickPick(DOCUMENT_TYPES, {
      placeHolder: 'Select document type...'
    });
    if (!picked) return;
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('No active editor');
      return;
    }
    const document = editor.document;
    const text = document.getText();
    const doctypeRegex = /doctype\s*=\s*[\w-]+/;
    
    if (doctypeRegex.test(text)) {
      const newText = text.replace(doctypeRegex, `doctype=${picked}`);
      await editor.edit(editBuilder => {
        editBuilder.replace(doctypeRegex.exec(text)![0], `doctype=${picked}`);
      });
      vscode.window.showInformationMessage(`Document type set to: ${picked}`);
    } else {
      vscode.window.showWarningMessage(
        'No doctype= found in documentclass options.',
        'Add `doctype=' + picked + '` to your \\documentclass options.'
      );
    }
  });

  const switchInstitution = vscode.commands.registerCommand('omnilatex.switchInstitution', async () => {
    const picked = await vscode.window.showQuickPick(INSTITUTIONS, {
      placeHolder: 'Select institution...'
    });
    if (!picked) return;
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('No active editor');
      return;
    }
    const document = editor.document;
    const text = document.getText();
    const instRegex = /institution\s*=\s*[\w-]+/;
    
    if (instRegex.test(text)) {
      await editor.edit(editBuilder => {
        editBuilder.replace(instRegex.exec(text)![0], `institution=${picked}`);
      });
      vscode.window.showInformationMessage(`Institution set to: ${picked}`);
    } else {
      vscode.window.showWarningMessage(
        'No institution= found in documentclass options.',
        'Add `institution=' + picked + '` to your \\documentclass options.'
      );
    }
  });

  const buildDoc = vscode.commands.registerCommand('omnilatex.build', async () => {
    vscode.window.showInformationMessage(
      'Build with: python3 build.py build-example <name>',
      'Or use the Terminal to run: python3 build.py build-all'
    );
  });

  const buildAll = vscode.commands.registerCommand('omnilatex.buildAll', async () => {
    vscode.window.showInformationMessage(
      'Build all with: python3 build.py build-all --timings',
      'This compiles all 42 examples and generates timing data.'
    );
  });

  context.subscriptions.push(
    vscode.languages.onDidChangeActiveTextEditor(() => {
      // Could add real-time doctype detection here
    })
  );

  context.statusBarItem = vscode.languages.createLanguageStatusItem('omnilatex.doctype');
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
