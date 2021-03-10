using AutoMapper;
using FinanceASP.NETCore.Authorization;
using FinanceASP.NETCore.Dtos;
using FinanceASP.NETCore.Models;
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
    public class AuthController : ControllerBase
    {
        private readonly UserManager<User> _userManager;
        private readonly SignInManager<User> _signInManager;
        private readonly IMapper _mapper;
        private readonly IConfiguration _config;

        public AuthController(UserManager<User> userManager, SignInManager<User> signInManager, IMapper mapper, IConfiguration config)
        {
            _userManager = userManager;
            _signInManager = signInManager;
            _mapper = mapper;
            _config = config;
        }


        // POST api/<AuthController>

        [HttpPost("login")]
        public async Task<IActionResult> Login(UserForLoginDto userForLoginDto)
        {
            var user = await _userManager.FindByEmailAsync(userForLoginDto.Email);

            var result = await _signInManager.CheckPasswordSignInAsync(user, userForLoginDto.Password, false);

            if (result.Succeeded)
            {
                //TODO
                //map dto with user data to avoid exposing too much information in the token
                var userForToken = _mapper.Map<UserMinimalInfoDto>(user);
                return Ok(new
                {
                    token = JwtToken.GenerateJwtToken(user, _config),
                    userForToken
                }
                //TODO
                //Data to send to client - JWt, cookie data, logged user data
                );
            }

            return Unauthorized();
        }

        [HttpPost("register")]
        public async Task<IActionResult> Register(UserForRegisterDto userForRegisterDto)
        {
            var userExists = await _userManager.FindByEmailAsync(userForRegisterDto.Email);

            if (!(userExists == null))
            {
                return BadRequest("This email is already registered.");
            }
            // var userToCreate = _mapper.Map<User>(userForRegisterDto);
            User userToCreate = new User();
            userToCreate.UserName = userForRegisterDto.UserName;
            userToCreate.Email = userForRegisterDto.Email;

            var result = await _userManager.CreateAsync(userToCreate, userForRegisterDto.Password);

            return StatusCode(201);
        }
    }
}
