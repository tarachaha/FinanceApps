using AutoMapper;
using FinanceASP.NETCore.Authorization;
using FinanceASP.NETCore.Dtos;
using FinanceASP.NETCore.Models;
using FinanceASP.NETCore.Repositories;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

// For more information on enabling Web API for empty projects, visit https://go.microsoft.com/fwlink/?LinkID=397860

namespace FinanceASP.NETCore.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class TransactionController : ControllerBase
    {
        private readonly UserManager<User> _userManager;
        private readonly SignInManager<User> _signInManager;
        private readonly IMapper _mapper;
        private readonly IConfiguration _config;
        private readonly IHoldingsRepository _repo;

        public TransactionController(UserManager<User> userManager,
        SignInManager<User> signInManager, IMapper mapper, 
        IConfiguration config, IHoldingsRepository repo)
        {
            _userManager = userManager;
            _signInManager = signInManager;
            _mapper = mapper;
            _config = config;
            _repo = repo;
        }

        [HttpGet("getHoldings")]
        public async Task<IActionResult> GetHoldings(UserMinimalInfoDto userDto)
        {
            List<Holdings> userHoldings = await _repo.GetHoldings(userDto.Id);
            return Ok(userHoldings);
        }
        
        [HttpPost("sell")]
        public async Task<IActionResult> Sell(UserMinimalInfoDto userDto, string stockName, int quantity)
        {
            bool canSell = await _repo.SellStock(userDto.Id, stockName, quantity);
            if(canSell)
            {
                return Ok();
            }else
            {
                return BadRequest();
            }
        }

        [HttpPost("buy")]
        public async Task<IActionResult> Buy(UserMinimalInfoDto userDto, string stockName, int quantity)
        {
            bool canBuy = await _repo.BuyStock(userDto.Id, stockName, quantity);
            if(canBuy)
            {
                return Ok();
            }else
            {
                return BadRequest();
            }
        }
    }
}