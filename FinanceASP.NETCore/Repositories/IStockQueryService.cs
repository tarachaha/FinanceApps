using System.Threading.Tasks;

namespace FinanceASP.NETCore.Repositories
{
    public interface IStockQueryService
    {
        Task<double> GetStockPrice();
    }
}