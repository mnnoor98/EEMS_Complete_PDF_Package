using EEMS.SharedKernel.Domain;

namespace EEMS.Modules.Elections.Domain;

public sealed class ElectionLifecycleState : Entity<short>
{
    private ElectionLifecycleState() { }
    private ElectionLifecycleState(short id,string code,string name,bool isTerminal){if(id<=0)throw new ArgumentOutOfRangeException(nameof(id));Id=id;Code=Require(code,40).ToUpperInvariant();Name=Require(name,100);IsTerminal=isTerminal;IsActive=true;}
    public string Code{get;private set;}=string.Empty; public string Name{get;private set;}=string.Empty; public bool IsTerminal{get;private set;} public bool IsActive{get;private set;}
    public static ElectionLifecycleState Create(short id,string code,string name,bool isTerminal)=>new(id,code,name,isTerminal);
    private static string Require(string value,int max){var text=value?.Trim()??string.Empty;return text.Length is >0&&text.Length<=max?text:throw new ArgumentException("Value is invalid.");}
}
