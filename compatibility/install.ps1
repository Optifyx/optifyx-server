$OS = $env:OS

if ($IsLinux) {
    Write-Host "Linux detected"
    pip install -r requirements/requirements-linux.txt
}
elseif ($IsMacOS) {
    Write-Host "macOS detected"
    pip install -r requirements/requirements-mac.txt
}
elseif ($OS -like "*Windows_NT*") {
    Write-Host "Windows detected"
    pip install -r requirements/requirements-win.txt
}
else {
    Write-Host "Unsupported system"
    exit 1
}

function IsLinux {
    return $IsLinux
}

function IsMacOS {
    return $IsMacOS
}

try {
    $uname = (uname) 2>$null
    if ($uname -eq "Linux") {
        $script:IsLinux = $true
    }
    elseif ($uname -eq "Darwin") {
        $script:IsMacOS = $true
    }
} catch {
    $script:IsLinux = $false
    $script:IsMacOS = $false
}