@{
    # Repository-level PSScriptAnalyzer settings
    # - Customize this file to include/exclude rules or change severities.
    # - See: https://learn.microsoft.com/powershell/utility-modules/psscriptanalyzer/overview

    # Use the default built-in rules unless explicitly excluded.
    ApplyDefaultRules = $true

    # Example severity overrides. Adjust per-repo as you harden the codebase.
    Severity = @{
        # Mark dangerous patterns as errors by default
        PSAvoidUsingInvokeExpression = 'Error'
        PSAvoidUsingPlainTextForPassword = 'Error'
        PSAvoidUsingConvertToSecureStringWithPlainText = 'Warning'
    }

    # Exclude rules that are noisy for documentation/example scripts.
    ExcludeRules = @(
        'PSAvoidUsingCmdletAliases'  # examples often use aliases for brevity
    )

    # Per-file or per-path suppressions can be added here as needed.
    Suppressions = @(
        # @{ RuleName = 'PSAvoidUsingCmdletAliases'; FilePath = 'reference-repositories/third_party/**'; Reason = 'Examples use aliases for readability' }
    )
}
