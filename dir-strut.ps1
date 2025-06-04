param (
    [string]$DirectoryPath = ".",
    [string]$OutputFile = "directory_structure.txt"
)

# Directories to skip
$skipDirs = @(
    ".venv",
    "venv",
    "node_modules",
    ".git",
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
    ".vscode",
    "bin",
    "obj",
    ".idea"
)

function Write-DirectoryStructure {
    param (
        [string]$Path,
        [int]$Depth = 0
    )
    
    $indent = "    " * $Depth
    $items = Get-ChildItem -Path $Path -ErrorAction SilentlyContinue
    
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            # Skip excluded directories
            if ($skipDirs -contains $item.Name) {
                continue
            }
            
            # Write directory name
            $script:output += "$indent<dir>$($item.Name)</dir>`n"
            Write-DirectoryStructure -Path $item.FullName -Depth ($Depth + 1)
        }
        else {
            # Write file name
            $script:output += "$indent<file>$($item.Name)</file>`n"
        }
    }
}

# Initialize output
$output = "<structure>`n"

# Process the directory structure
Write-DirectoryStructure -Path $DirectoryPath

# Close the structure
$output += "</structure>"

# Write the output to a file
$output | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "Directory structure has been saved to $OutputFile"